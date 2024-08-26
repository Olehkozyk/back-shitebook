from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    title = models.CharField(max_length=255, default='Untitled Chat')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.title:
            return f"Chat {self.title} between {', '.join([user.username for user in self.participants.all()])}"
        return f"Chat {self.id} between {', '.join([user.username for user in self.participants.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message {self.id} by {self.sender.username} in Chat {self.chat.id}"