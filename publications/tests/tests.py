from datetime import datetime, timedelta
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.urls import reverse

from pytest import fixture, mark
from rest_framework import status
from rest_framework.test import APIClient

from publications.models import Publication
from publications.signals import update_user_comments_count, update_user_publications_count
from publications.tests.factories import PublicationCommentFactory, PublicationFactory
from users.tests.factories import UserFactory

User = get_user_model()


class TestPublicationModelViewSet:
    @fixture(autouse=True)
    def set_up(self):
        self.user = UserFactory(username="tester", email="tester@localhost.com")
        self.user.set_password(self.user.username)
        self.user.save()

        self.reverse_name = "publications"
        self.client = APIClient()

    # private methods
    def _get_auth_token_headers(self):
        response = self.client.post(
            reverse("api_token_auth"),
            data={"username": self.user.username, "password": self.user.username},
            format="json",
        )
        return {"Authorization": f"Token {response.data.get('token')}"}

    def _post_data(self, data, authenticate=True):
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.post(reverse(f"{self.reverse_name}-list"), data, headers=headers, format="json")

    def _retrieve_data(self, pk, authenticate=True):
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.get(
            path=reverse(f"{self.reverse_name}-detail", kwargs={"pk": pk}), headers=headers, format="json"
        )

    def _list_data(self, query_params=None, authenticate=True):
        query_params_str = f"?{urlencode(query_params)}" if query_params else ""
        url = reverse(f"{self.reverse_name}-list")
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.get(f"{url}{query_params_str}", headers=headers, format="json")

    def _post_comment(self, pk, data, authenticate=True):
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.post(
            reverse(f"{self.reverse_name}-comments", kwargs={"pk": pk}), headers=headers, data=data, format="json"
        )

    def _get_comments(self, pk, authenticate=True):
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.get(
            reverse(f"{self.reverse_name}-comments", kwargs={"pk": pk}), headers=headers, format="json"
        )

    # tests
    @mark.success
    @mark.django_db
    def test_create_publication_success(self):
        assert Publication.objects.count() == 0
        assert self.user.publications_count == 0

        response = self._post_data(data={"title": "publication title", "content": "publication content"})

        assert response.data["author"] == self.user.id
        assert Publication.objects.count() == 1
        self.user.refresh_from_db()
        assert self.user.publications_count == 1
        assert response.status_code == status.HTTP_201_CREATED

    @mark.error
    @mark.django_db
    def test_create_publication_bad_data_error(self):
        assert Publication.objects.count() == 0
        assert self.user.publications_count == 0

        response = self._post_data(data={"title": True, "content": [1, 2, 3]})

        assert Publication.objects.count() == 0
        self.user.refresh_from_db()
        assert self.user.publications_count == 0
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @mark.success
    @mark.django_db
    def test_list_publications_success(self):
        pub_ids, now, user_2 = set(), datetime.now(), UserFactory()
        for num in range(21):
            pub = PublicationFactory(
                author=self.user if num % 2 == 0 else user_2, created=now - timedelta(days=num + 5)
            )
            pub_ids.add(pub.id)

        # check page_1 in the following steps:
        response = self._list_data()

        # fmt: off
        assert set(response.data.keys()) == {
            'next', 'page_number', 'page_size', 'previous', 'results', 'total_items', 'total_pages'
        }
        # fmt: on

        assert len(response.data["results"]) == 20

        page_1_ids = set(res["id"] for res in response.data["results"])
        assert page_1_ids.issubset(pub_ids)

        createds, createds_2 = list(), list()
        for res in response.data["results"]:
            assert set(res.keys()) == {"author", "content", "created", "id", "title"}
            createds.append(res["created"])
            createds_2.append(res["created"])

        createds_2.sort(reverse=True)
        assert createds == createds_2  # response.data["results"] is ordered from newest to oldest

        assert response.status_code == status.HTTP_200_OK

        # check page_2 in the following steps:
        response_page_2 = self._list_data(query_params={"page_number": 2})
        assert len(response_page_2.data["results"]) == 1

        page_2_ids = set(res["id"] for res in response_page_2.data["results"])
        assert page_2_ids == page_1_ids.symmetric_difference(pub_ids)

        # check "last created in page_1" is newest (major) than "first created in page_2"
        assert response_page_2.data["results"][0]["created"] < response.data["results"][-1]["created"]

        assert response.status_code == status.HTTP_200_OK

    @mark.success
    @mark.django_db
    def test_list_publications_with_filter_success(self):
        now, user_2 = datetime.now(), UserFactory()
        for num in (5, 10, 15, 20, 25, 30, 35, 40):
            PublicationFactory(author=self.user, created=now - timedelta(days=num))
            PublicationFactory(author=user_2, created=now - timedelta(days=num))

        from_date = now - timedelta(days=37)
        to_date = now - timedelta(days=7)

        query_params = {
            "author": self.user.id,
            "from_date": from_date.strftime("%d-%m-%Y"),
            "to_date": to_date.strftime("%d-%m-%Y"),
            "page_size": 4,
        }

        # check page_1 in the following steps:
        response = self._list_data(query_params=query_params)

        publications = Publication.objects.filter(
            author_id=self.user.id,
            created__gte=from_date,
            created__lte=to_date,
        ).order_by("-created")

        assert len(response.data["results"]) == 4

        filtered_pubs_ids = list(publications.values_list("id", flat=True))
        assert [res["id"] for res in response.data["results"]] == filtered_pubs_ids[:4]

        assert response.status_code == status.HTTP_200_OK

        # check page_2 in the following steps:
        response_page_2 = self._list_data(query_params={"page_number": 2} | query_params)
        assert [res["id"] for res in response_page_2.data["results"]] == filtered_pubs_ids[4:]
        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_list_without_auth(self):
        response = self._list_data(authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.success
    @mark.django_db
    def test_retrieve_publication_success(self):
        pub = PublicationFactory(author=self.user)

        comment_ids = list()
        for _ in range(5):
            comment = PublicationCommentFactory(author=self.user, publication=pub)
            comment_ids.append(comment.id)

        response = self._retrieve_data(pk=pub.id)
        assert set(response.data.keys()) == {"author", "last_3_comments", "publication"}

        # fmt: off
        assert set(response.data["author"].keys()) == {
            'comments_count', 'created', 'date_joined', 'email', 'first_name', 'id', 'is_active',
            'is_staff', 'is_superuser', 'last_login', 'last_name', 'publications_count',
            'username'
        }
        # fmt: on
        assert response.data["author"]["id"] == self.user.id

        for comment_data in response.data["last_3_comments"]:
            assert set(comment_data.keys()) == {"author", "content", "created", "id", "publication"}
            assert comment_data["publication"] == pub.id

        assert set(comment_data["id"] for comment_data in response.data["last_3_comments"]) == set(comment_ids[-3:])

        assert set(response.data["publication"].keys()) == {"author", "content", "created", "id", "title"}
        assert response.data["publication"]["id"] == pub.id

        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_retrieve_publication_without_auth(self):
        pub = PublicationFactory(author=self.user)
        response = self._retrieve_data(pk=pub.id, authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.success
    @mark.django_db
    def test_retrieve_publication_wrong_id(self):
        response = self._retrieve_data(pk=666)
        assert response.json()["detail"] == "No Publication matches the given query."
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @mark.success
    @mark.django_db
    def test_publication_comment_create_success(self):
        assert self.user.publications_count == 0

        pub = PublicationFactory(author=self.user)
        assert pub.comments.count() == 0

        self.user.refresh_from_db()
        assert self.user.publications_count == 1
        assert self.user.comments_count == 0

        response = self._post_comment(pub.id, data={"content": "this is a comment"})

        response.data["author"] == self.user.id
        assert pub.comments.count() == 1
        self.user.refresh_from_db()
        assert self.user.comments_count == 1
        assert response.status_code == status.HTTP_201_CREATED

    @mark.unauthorized
    @mark.django_db
    def test_publication_comment_without_auth(self):
        pub = PublicationFactory(author=self.user)
        response = self._post_comment(pub.id, data={"content": "this is a comment"}, authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.success
    @mark.django_db
    def test_publication_comments_get_success(self):
        assert self.user.publications_count == 0
        assert self.user.comments_count == 0

        pub = PublicationFactory(author=self.user)
        assert pub.comments.count() == 0

        comment_ids = set()
        for num in range(5):
            comment = PublicationCommentFactory(author=self.user, publication=pub, content=f"content {num}")
            comment_ids.add(comment.id)

        self.user.refresh_from_db()
        assert self.user.publications_count == 1
        assert self.user.comments_count == 5

        response = self._get_comments(pub.id)

        # fmt: off
        assert set(response.data.keys()) == {
            'next', 'page_number', 'page_size', 'previous', 'results', 'total_items', 'total_pages'
        }
        # fmt: on

        assert {item["id"] for item in response.data["results"]} == comment_ids
        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_publication_comments_get_without_auth(self):
        pub = PublicationFactory(author=self.user)
        response = self._get_comments(pub.id, authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
