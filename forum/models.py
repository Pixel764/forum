from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from users.models import CustomUserModel
from ckeditor.fields import RichTextField


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    def clean(self):
        if len(self.title.split(' ')) > 1:
            raise ValidationError('The title must be united. Example "%s"' % ('-'.join(self.title.split(' '))))
        super(Category, self).clean()


class Post(models.Model):
    category = models.ForeignKey(to=Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextField(max_length=20000)
    published_date = models.DateTimeField(auto_now_add=True)
    last_change_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(to=CustomUserModel, on_delete=models.CASCADE, blank=True)
    likes = models.ManyToManyField(to=CustomUserModel, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(to=CustomUserModel, related_name='disliked_posts', blank=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:post_page', kwargs={'post_pk': self.pk})


class Comment(models.Model):
    post = models.ForeignKey(to=Post, on_delete=models.CASCADE)
    text = models.TextField(max_length=1500)
    author = models.ForeignKey(to=CustomUserModel, on_delete=models.CASCADE)
    published_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-published_date']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('forum:post_page', kwargs={'post_pk': self.post.pk})
