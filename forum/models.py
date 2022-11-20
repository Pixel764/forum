from django.db import models
from django.urls import reverse
from users.models import CustomUserModel


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(max_length=20000)
    published_date = models.DateTimeField(auto_now_add=True)
    last_change_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(to=CustomUserModel, on_delete=models.CASCADE, blank=True)
    likes = models.ManyToManyField(to=CustomUserModel, related_name='liked_posts', blank=True)

    class Meta:
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
        ordering = ['-published_date']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('forum:post_page', kwargs={'post_pk': self.post.pk})
