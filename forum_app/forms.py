from django import forms
from django.core.exceptions import ValidationError

from .models import Post, Comment


class CreateAndEditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
