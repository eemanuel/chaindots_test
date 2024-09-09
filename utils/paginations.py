from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 20  # default items per page
    max_page_size = 100  # max items allowed per page
    page_query_param = "page_number"  # queryparam to change the page number
    page_size_query_param = "page_size"  # queryparam to change the amount of items per page

    def get_paginated_response(self, data):
        return Response(
            {
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "page_number": self.page.number,
                "page_size": self.page.paginator.per_page,
                "total_pages": self.page.paginator.num_pages,
                "total_items": self.page.paginator.count,
                "results": data,
            }
        )
