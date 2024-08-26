from rest_framework.pagination import PageNumberPagination

class PaginationPosts(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'


class CommentPagination(PageNumberPagination):
    page_size = 999
    page_size_query_param = 'page_size'