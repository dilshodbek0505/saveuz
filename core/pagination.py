"""
Единый формат пагинации для API: count, next, previous, results, page_size.
Используется мобильным приложением для единообразного отображения.
"""
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        response.data["page_size"] = self.get_page_size(self.request)
        return response
