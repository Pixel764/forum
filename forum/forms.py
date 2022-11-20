from django import forms
from .models import Post, Comment
from ckeditor.fields import CKEditorWidget


class CreateAndEditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            #'content': forms.Textarea(attrs={'class': 'form-control inline-block', 'style': 'resize:none'})
            'content': CKEditorWidget(attrs={'style': 'width: 100%;'})
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
