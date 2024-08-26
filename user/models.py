from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url

from chats.models import Chat


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True)
    avatar = CloudinaryField('Avatar',
                             overwrite=True,
                             resource_type="image",
                             transformation={"quality": "auto:eco"},
                             null=True,
                             blank=True
                             )
    online_status = models.BooleanField(default=False)
    avatar_id = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.avatar:
            self.avatar_id = self.avatar.public_id
            self.avatar_url = cloudinary_url(self.avatar.public_id)[0]
            super().save(update_fields=['avatar_id', 'avatar_url'])

    def __str__(self):
        return self.user.username


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def accept(self):
        self.accepted = True
        self.save()
        from_user_friends = self.from_user.user_friends
        to_user_friends = self.to_user.user_friends

        from_user_friends.friends.add(self.to_user)
        to_user_friends.friends.add(self.from_user)

        chat = Chat.objects.filter(participants=self.from_user).filter(participants=self.to_user).first()

        if chat is None:
            chat = Chat.objects.create(title=f"Chat between {self.from_user.username} and {self.to_user.username}")
            chat.participants.add(self.from_user, self.to_user)

        self.delete()

    def reject(self):
        self.delete()

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"


class UserFriend(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_friends')
    friends = models.ManyToManyField(User, related_name='friend_of', blank=True)
    friend_requests = models.ManyToManyField(FriendRequest, related_name='user_friend_requests', blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile_and_friends(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
        UserFriend.objects.get_or_create(user=instance)
