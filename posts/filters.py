from django_filters import rest_framework as filters
from django.db.models import Q

from posts.models import Post


class PostsFilter(filters.FilterSet):
    search = filters.CharFilter(method='filter_by_title_or_description')

    class Meta:
        model = Post
        fields = ['search']

    def filter_by_title_or_description(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))