from django.contrib import admin
from .models import Chat, Message
from .form import ChatAdminForm, MessageAdminForm

class ChatModelAdmin(admin.ModelAdmin):
    form = ChatAdminForm
    list_per_page = 5

class MessageModelAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    list_per_page = 5


admin.site.register(Chat, ChatModelAdmin)
admin.site.register(Message, MessageModelAdmin)
