from rest_framework import serializers
from forum.models import Post
from django.utils import timezone


class PostSerializer(serializers.ModelSerializer):
	author_username = serializers.SerializerMethodField()
	likes_amount = serializers.SerializerMethodField()

	class Meta:
		model = Post
		exclude = ['likes', 'author']
		read_only = ['id', 'published_date', 'last_change_date', 'author_username', 'likes_amount']

	def get_author_username(self, obj):
		return obj.author.username

	def get_likes_amount(self, obj):
		return obj.likes.count()

	def create(self, validated_data):
		return Post.objects.create(**validated_data, author=self.context['author'])

	def update(self, instance, validated_data):
		instance.title = validated_data.get('title', instance.title)
		instance.content = validated_data.get('content', instance.content)
		instance.last_change_date = timezone.now()
		instance.save()
		return instance
