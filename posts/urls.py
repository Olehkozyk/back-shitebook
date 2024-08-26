from django.urls import path
from .views import (
    PostListUserView,
    PostListView,
    PostCreateView,
    PostRetrieveView,
    PostUpdateView,
    PostDeleteView, PostCommentView, PostLikeView, CommentCreateView,
)

urlpatterns = [
    # Get List #GET
    path('/', PostListUserView.as_view(), name='post-list-user'),
    path('/list/', PostListView.as_view(), name='post-list'),

    path('/<int:post_id>/comments/', PostCommentView.as_view(), name='post-comments'),
    path('/comment/create/', CommentCreateView.as_view(), name='comment-create'),

    path('/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    # Create view #POST
    path('/create/', PostCreateView.as_view(), name='post-create'),

    # Retrieve view (Read one) #GET
    path('/<int:pk>/', PostRetrieveView.as_view(), name='post-retrieve'),

    # Update view #PUT
    path('/update/<int:pk>/', PostUpdateView.as_view(), name='post-update'),

    # Delete view #DELETE
    path('/delete/<int:pk>/', PostDeleteView.as_view(), name='post-destroy'),
]
