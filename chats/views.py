from django.shortcuts import get_object_or_404
from .models import Chat
from .serializers import ChatSerializer
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    UpdateAPIView, # new
    DestroyAPIView, # new
)
from rest_framework.permissions import IsAuthenticated

# Create view
class ChatCreateView(CreateAPIView):
    serializer_class = ChatSerializer

# List view
class ChatListView(ListAPIView):
    serializer_class = ChatSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

# Retrieve view
class ChatRetrieveView(RetrieveAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

# Update view
class ChatUpdateView(UpdateAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

# Delete view
class ChatDeleteView(DestroyAPIView):
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()

