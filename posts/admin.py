from django.contrib import admin
from .models import Post, Comment

class PostsModelAdmin(admin.ModelAdmin):
    readonly_fields = ('image_id', 'image_url')
    list_display = ('title', 'updated_at', 'created_at',)
    search_fields = ('title', 'description',)
    list_per_page = 5

class ComentsPostModelAdmin(admin.ModelAdmin):
        list_display = ('post', 'content', 'author',)
        search_fields = ('post', 'content', 'author',)
        list_per_page = 5

admin.site.register(Comment, ComentsPostModelAdmin)
admin.site.register(Post, PostsModelAdmin)
