from django.db import models
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url
from django.contrib.auth.models import User
# Create your models here.
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = CloudinaryField('Image',
                            overwrite=True,
                            resource_type="image",
                            transformation={"quality": "auto:eco"},
                            )
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    image_id = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            self.image_id = self.image.public_id
            self.image_url = cloudinary_url(self.image.public_id)[0]
            super().save(update_fields=['image_id', 'image_url'])

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'