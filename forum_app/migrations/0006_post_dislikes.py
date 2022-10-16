# Generated by Django 4.1.1 on 2022-10-16 11:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('forum_app', '0005_post_likes_alter_comment_table_alter_post_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='dislikes',
            field=models.ManyToManyField(related_name='disliked_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]
