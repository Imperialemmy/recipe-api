from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 3  # Default items per page
    page_size_query_param = 'page_size'  # Allows users to specify page size
    max_page_size = 6  # Limits max items per page

class ProductsPagePagination(PageNumberPagination):
    page_size = 5  # Default items per page
    page_size_query_param = 'page_size'  # Allows users to specify page size
    max_page_size = 10  # Limits max items per page