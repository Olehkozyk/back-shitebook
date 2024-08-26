from django import forms
from .models import Chat, Message

class ChatAdminForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ['title', 'participants']

    def clean_participants(self):
        participants = self.cleaned_data.get('participants')

        if participants.count() < 2:
            raise forms.ValidationError("A chat must have at least two participants.")

        if participants.count() != len(set(participants)):
            raise forms.ValidationError("Participants must be unique.")

        existing_chats = Chat.objects.filter(participants__in=participants).distinct()
        for chat in existing_chats:
            if set(chat.participants.all()) == set(participants):
                raise forms.ValidationError("A chat with these participants already exists.")

        return participants

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError("The title is required.")
        return title

class MessageAdminForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        chat = cleaned_data.get('chat')
        sender = cleaned_data.get('sender')

        if sender not in chat.participants.all():
            raise forms.ValidationError("The sender must be a participant in the chat.")

        return cleaned_data