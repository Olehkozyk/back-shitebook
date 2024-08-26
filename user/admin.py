from django.contrib import admin
from .models import UserProfile, UserFriend, FriendRequest


class UserProfileModelAdmin(admin.ModelAdmin):
    readonly_fields = ('avatar_id', 'avatar_url')
    list_display = ('user_id',)
    search_fields = ('birth_date',)
    list_per_page = 5

class UserFriendsModelAdmin(admin.ModelAdmin):
    # readonly_fields = ('user', 'friends')
    list_display = ('user',)
    list_per_page = 5


class UserFriendsRequsetModelAdmin(admin.ModelAdmin):
    # readonly_fields = ('user', 'friends')
    list_display = ('from_user', 'to_user')
    list_per_page = 5

admin.site.register(FriendRequest, UserFriendsRequsetModelAdmin)
admin.site.register(UserProfile, UserProfileModelAdmin)
admin.site.register(UserFriend, UserFriendsModelAdmin)
