from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.urls import reverse

from pytest import fixture, mark
from rest_framework import status
from rest_framework.test import APIClient

from users.tests.factories import UserFactory

User = get_user_model()


class TestUserModelViewSet:
    @fixture(autouse=True)
    def set_up(self):
        self.user = UserFactory(username="tester", email="tester@localhost.com")
        self.user.set_password(self.user.username)
        self.user.save()

        self.reverse_name = "users"
        self.client = APIClient()

    # private methods
    def _get_auth_token_headers(self):
        response = self.client.post(
            reverse("api_token_auth"),
            data={"username": self.user.username, "password": self.user.username},
            format="json",
        )
        return {"Authorization": f"Token {response.data.get('token')}"}

    def _post_data(self, data):  # without authentication required
        return self.client.post(reverse(f"{self.reverse_name}-list"), data, format="json")

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

    def _post_follow(self, pk, followed_pk, authenticate=True):
        headers = self._get_auth_token_headers() if authenticate else dict()
        return self.client.post(
            reverse(f"{self.reverse_name}-follow", kwargs={"pk": pk, "followed_pk": followed_pk}),
            headers=headers,
            format="json",
        )

    # tests
    @mark.success
    @mark.django_db
    def test_create_success(self):
        assert User.objects.count() == 1  # self.user exists!

        response = self._post_data(
            data={"username": "test_username", "password": "test_username", "email": "test_username@localhost.com"}
        )

        assert User.objects.count() == 2
        assert response.status_code == status.HTTP_201_CREATED

    @mark.error
    @mark.django_db
    def test_create_bad_data_error(self):
        assert User.objects.count() == 1  # self.user exists!
        response = self._post_data(data={"username": True, "email": [1, 2, 3]})
        assert User.objects.count() == 1
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @mark.success
    @mark.django_db
    def test_list_success(self):
        ids = [self.user.id]
        for _ in range(2):
            instance = UserFactory()
            ids.append(instance.id)

        response = self._list_data()

        assert set(response.data.keys()) == {
            "next",
            "previous",
            "page_number",
            "page_size",
            "total_pages",
            "total_items",
            "results",
        }

        for item in response.data["results"]:
            assert item["id"] in ids
            for field in ["username", "email"]:
                assert item[field] is not None, field
        assert response.status_code == status.HTTP_200_OK

    @mark.success
    @mark.django_db
    def test_list_with_filter_success(self):
        UserFactory(username="another user")

        response = self._list_data(query_params={"username": "test"})

        assert set(response.data.keys()) == {
            "next",
            "previous",
            "page_number",
            "page_size",
            "total_pages",
            "total_items",
            "results",
        }
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["id"] == self.user.id
        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_list_without_auth(self):
        response = self._list_data(authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.success
    @mark.django_db
    def test_retrieve_success(self):
        response = self._retrieve_data(pk=self.user.id)
        assert set(response.data.keys()) == {
            "comments_count",
            "created",
            "date_joined",
            "email",
            "first_name",
            "followers",
            "following",
            "id",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "last_name",
            "password",
            "publications_count",
            "username",
        }
        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_retrieve_without_auth(self):
        response = self._retrieve_data(pk=self.user.id, authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @mark.success
    @mark.django_db
    def test_retrieve_wrong_id(self):
        response = self._retrieve_data(pk=666)
        assert response.json()["detail"] == "No User matches the given query."
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @mark.success
    @mark.django_db
    def test_follow_success(self):
        followed = UserFactory(username="followed user", email="followd@localhost.com")

        assert self.user.following.count() == 0
        assert followed.followers.count() == 0

        response = self._post_follow(self.user.id, followed.id)

        assert self.user.following.count() == 1
        assert followed.followers.count() == 1

        assert self.user.following.first() == followed
        assert followed.followers.first() == self.user

        assert response.data["message"] == f"User with id={self.user.id} is now following User with id={followed.id}."
        assert response.status_code == status.HTTP_200_OK

    @mark.unauthorized
    @mark.django_db
    def test_follow_without_auth(self):
        followed = UserFactory(username="followed user", email="followd@localhost.com")
        response = self._post_follow(self.user.id, followed.id, authenticate=False)
        assert response.json()["detail"] == "Authentication credentials were not provided."
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
