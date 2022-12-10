from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import UpdateIfAuthorOrAdmin
from forum.models import Post, Category
from .serializers import PostSerializer, CategorySerializer
from .pagination import PostPagination
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView


class PostCRUDAPI(ModelViewSet):
	queryset = Post.objects.all()
	serializer_class = PostSerializer
	pagination_class = PostPagination
	permission_classes = [IsAuthenticatedOrReadOnly, UpdateIfAuthorOrAdmin]

	def list(self, request, *args, **kwargs):
		if 'amount' in kwargs:
			self.queryset = self.queryset[:kwargs.get('amount')]

		page = self.paginate_queryset(self.queryset)
		serializer = self.get_serializer(page, many=True)
		return self.get_paginated_response(serializer.data)

	def retrieve(self, request, *args, **kwargs):
		try:
			obj = Post.objects.get(pk=kwargs.get('pk'))
		except:
			return Response({'error': 'Object doesnt exists'})
		else:
			return Response({'post': self.serializer_class(obj).data})

	def destroy(self, request, *args, **kwargs):
		try:
			obj = Post.objects.get(pk=kwargs.get('pk'))
		except:
			return Response({'error': 'Object doesnt exists'})
		else:
			self.check_object_permissions(request, obj)
			obj.delete()
			return Response({'info': f'Post is deleted'})

	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'author': request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'created-post': serializer.data})

	def update(self, request, *args, **kwargs):
		try:
			obj = Post.objects.get(pk=kwargs.get('pk'))
		except:
			return Response({'error': 'Object doesnt exists'})
		else:
			self.check_object_permissions(request, obj)
			serializer = self.serializer_class(data=request.data, instance=obj, partial=True)
			serializer.is_valid(raise_exception=True)
			serializer.save()
			return Response({'post': serializer.data})


class PostRatingAPI(RetrieveAPIView):
	queryset = Post.objects.all()
	accepted_status = ['like', 'dislike']
	permission_classes = [IsAuthenticated]

	def get(self, request, *args, **kwargs):
		if kwargs['status'] not in self.accepted_status:
			Response({'error': f"Invalid status \"{kwargs['status']}\". Accepted only ['like', 'dislike']"})

		return self.retrieve(request, *args, **kwargs)

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()

		if kwargs['status'] == 'like':
			self.set_like(instance, request.user)
		else:
			self.set_dislike(instance, request.user)

		return Response({'likes': instance.likes.count(), 'dislikes': instance.dislikes.count()})

	@staticmethod
	def set_like(post, user):
		if post.likes.filter(pk=user.pk):
			post.likes.remove(user)
		else:
			if post.dislikes.filter(pk=user.pk):
				post.dislikes.remove(user)
			post.likes.add(user)

	@staticmethod
	def set_dislike(post, user):
		if post.dislikes.filter(pk=user.pk):
			post.dislikes.remove(user)
		else:
			if post.likes.filter(pk=user.pk):
				post.likes.remove(user)
			post.dislikes.add(user)


class CategoryAPI(ModelViewSet):
	queryset = Category.objects.all()
	pagination_class = PostPagination
	serializer_class = CategorySerializer

	def retrieve(self, request, *args, **kwargs):
		category = self.get_object()
		queryset = category.post_set.all()
		page = self.paginate_queryset(queryset)
		serializer = PostSerializer(page, many=True)
		return self.paginator.get_paginated_response(serializer.data)


class UserPostsAPI(GenericAPIView):
	queryset = Post.objects.all()
	pagination_class = PostPagination
	serializer_class = PostSerializer

	def get(self, request, *args, **kwargs):
		queryset = self.queryset.filter(author__username=kwargs.get('username'))

		if 'amount' in kwargs:
			queryset = queryset[:kwargs.get('amount')]

		page = self.paginate_queryset(queryset)
		serializer = self.serializer_class(page, many=True)
		return self.paginator.get_paginated_response(serializer.data)
