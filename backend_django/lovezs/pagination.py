from rest_framework.pagination import PageNumberPagination


class PageSizePagination(PageNumberPagination):
    """Page number pagination with page_size and legacy limit support."""

    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_page_size(self, request):
        legacy_limit = request.query_params.get('limit')
        if legacy_limit is not None:
            try:
                page_size = int(legacy_limit)
            except (TypeError, ValueError):
                return super().get_page_size(request)

            if page_size > 0:
                return min(page_size, self.max_page_size)

        return super().get_page_size(request)
