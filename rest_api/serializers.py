from rest_framework import serializers
from forum.models import Post, Category, Comment
from django.utils import timezone


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = []
        read_only = ['id', 'title']


class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    likes_amount = serializers.SerializerMethodField()
    dislikes_amount = serializers.SerializerMethodField()

    class Meta:
        model = Post
        exclude = ['likes', 'dislikes', 'author']
        read_only = ['id', 'published_date', 'last_change_date', 'author_username', 'likes_amount', 'dislikes_amount']

    def get_author_username(self, obj):
        return obj.author.username

    def get_likes_amount(self, obj):
        return obj.likes.count()

    def get_dislikes_amount(self, obj):
        return obj.dislikes.count()

    def create(self, validated_data):
        return Post.objects.create(**validated_data, author=self.context['author'])

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.category = validated_data.get('category', instance.category)
        instance.last_change_date = timezone.now()
        instance.save()
        return instance


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()
    likes_amount = serializers.SerializerMethodField()
    dislikes_amount = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        exclude = ['author', 'dislikes', 'likes']
        read_only = ['author_username', 'last_change_date', 'published_date']

    def get_author_username(self, obj):
        return obj.author.username

    def get_likes_amount(self, obj):
        return obj.likes.count()

    def get_dislikes_amount(self, obj):
        return obj.dislikes.count()

    def create(self, validated_data):
        return Comment.objects.create(**validated_data, author=self.context['author'])

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.post = validated_data.get('post', instance.post)
        instance.last_change_date = timezone.now()
        instance.save()
        return instance
