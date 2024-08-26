from django.urls import path
from .views import (
    UserDetailView,
    UserLoginView,
    UserRegisterView,
    CurrentUserDetailView,
    UserListView,
    UserAddFriendView,
    UserRemoveFriendRequestView,
    SentFriendRequestsView,
    AcceptFriendRequestView,
    IsFriendView,
    RemoveFriendView,
    FriendListView
)

urlpatterns = [
    # profile user by id
    path('/profile/<int:pk>/', UserDetailView.as_view(), name='user-profile-retrieve'),

    # profile loggined user
    path('/profile/', CurrentUserDetailView.as_view(), name='user-profile'),

    # list users
    path('/list/', UserListView.as_view(), name='user-list'),

    # request friends
    path('/add-friend/', UserAddFriendView.as_view(), name='add-friend'),
    path('/is-friend/', IsFriendView.as_view(), name='is-friend'),
    path('/friend-list/', FriendListView.as_view(), name='friend-list'),
    path('/accept-friend/', AcceptFriendRequestView.as_view(), name='accept-friend'),
    path('/remove-friend/', RemoveFriendView.as_view(), name='remove-friend'),
    path('/remove-request-friend/', UserRemoveFriendRequestView.as_view(), name='remove-request-friend'),
    path('/friend-requests/', SentFriendRequestsView.as_view(), name='sent-friend-requests'),

    # auth path
    path('/register/', UserRegisterView.as_view(), name='register'),
    path('/login/', UserLoginView.as_view(), name='login'),
]
