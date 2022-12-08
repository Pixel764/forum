from django import forms
from .models import Post, Comment


class CreateAndEditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'category', 'content']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select form-select-sm'})
        }


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = 'Comment'

    class Meta:
        model = Comment
        fields = ['text']

        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'style': 'resize:none'})
        }
