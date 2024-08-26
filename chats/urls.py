from django.urls import path
from .views import ChatCreateView, ChatListView, ChatRetrieveView, ChatUpdateView, ChatDeleteView
urlpatterns = [
    #Get List #GET
    path('/', ChatListView.as_view(), name='сhat-list'),

    # Create view #POST
    path('/create/', ChatCreateView.as_view(), name='сhat-create'),

    # Retrieve view (Read one) #GET
    path('/<int:pk>/', ChatRetrieveView.as_view(), name='сhat-retrieve'),

    # Update view #PUT
    path('/update/<int:pk>/', ChatUpdateView.as_view(), name='сhat-update'),

    # Delete view #DELETE
    path('/delete/<int:pk>/', ChatDeleteView.as_view(), name='сhat-destroy'),
]