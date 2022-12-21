from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from users.models import CustomUserModel
from ckeditor.fields import RichTextField


class AbstractDateAndRating(models.Model):
    published_date = models.DateTimeField(auto_now_add=True)
    last_change_date = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(CustomUserModel, related_name='%(class)ss_likes', blank=True)
    dislikes = models.ManyToManyField(CustomUserModel, related_name='%(class)ss_dislikes', blank=True)

    class Meta:
        abstract = True


class Category(models.Model):
    title = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['-pk']

    def __str__(self):
        return self.title

    def clean(self):
        if len(self.title.split(' ')) > 1:
            raise ValidationError('The title must be united. Example "%s"' % ('-'.join(self.title.split(' '))))
        super(Category, self).clean()


class Post(AbstractDateAndRating):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = RichTextField(max_length=20000)
    author = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'posts'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:post_page', kwargs={'post_pk': self.pk})


class Comment(AbstractDateAndRating):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField(max_length=1500)
    author = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'comments'
        ordering = ['-published_date']

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('forum:post_page', kwargs={'post_pk': self.post.pk}) + f'#comment_{self.pk}'
