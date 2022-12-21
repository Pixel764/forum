from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from .permissions import UpdateIfAuthorOrAdmin
from forum.models import Post, Category, Comment
from .serializers import PostSerializer, CategorySerializer, CommentSerializer
from .pagination import CustomPagination
from rest_framework.generics import GenericAPIView
from django.shortcuts import get_object_or_404


class CategoryAPI(ModelViewSet):
	queryset = Category.objects.all()
	pagination_class = CustomPagination
	serializer_class = CategorySerializer

	def retrieve(self, request, *args, **kwargs):
		category = self.get_object()
		queryset = category.post_set.all()
		page = self.paginate_queryset(queryset)
		serializer = PostSerializer(page, many=True)
		return self.paginator.get_paginated_response(serializer.data)


class RatingAPI(APIView):
	model = None
	accepted_status = ['like', 'dislike']
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		if kwargs['status'] not in self.accepted_status:
			Response({'error': f"Invalid status \"{kwargs['status']}\". Accepted only ['like', 'dislike']"})
		return self.update(request, *args, **kwargs)

	def update(self, request, *args, **kwargs):
		instance = self.get_object()

		if kwargs['status'] == 'like':
			self.set_like(instance, request.user)
		else:
			self.set_dislike(instance, request.user)

		return Response({'likes': instance.likes.count(), 'dislikes': instance.dislikes.count()})

	def get_object(self):
		obj = get_object_or_404(self.model, pk=self.kwargs['pk'])
		return obj

	@staticmethod
	def set_like(obj, user):
		if obj.likes.filter(pk=user.pk):
			obj.likes.remove(user)
		else:
			if obj.dislikes.filter(pk=user.pk):
				obj.dislikes.remove(user)
			obj.likes.add(user)

	@staticmethod
	def set_dislike(obj, user):
		if obj.dislikes.filter(pk=user.pk):
			obj.dislikes.remove(user)
		else:
			if obj.likes.filter(pk=user.pk):
				obj.likes.remove(user)
			obj.dislikes.add(user)


class PostAPI(ModelViewSet):
	queryset = Post.objects.all()
	serializer_class = PostSerializer
	pagination_class = CustomPagination
	permission_classes = [IsAuthenticatedOrReadOnly, UpdateIfAuthorOrAdmin]

	def list(self, request, *args, **kwargs):
		page = self.paginate_queryset(self.queryset)
		serializer = self.get_serializer(page, many=True)
		return self.get_paginated_response(serializer.data)

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.serializer_class(instance)
		return Response({'post': serializer.data})

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		self.check_object_permissions(request, instance)
		instance.delete()
		return Response({'info': f'Post is deleted'})

	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'author': request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'created-post': serializer.data})

	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		self.check_object_permissions(request, instance)
		serializer = self.serializer_class(data=request.data, instance=instance, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'post': serializer.data})


class PostRatingAPI(RatingAPI):
	model = Post


class CommentAPI(ModelViewSet):
	queryset = Comment.objects.all()
	pagination_class = CustomPagination
	serializer_class = CommentSerializer
	permission_classes = [IsAuthenticatedOrReadOnly, UpdateIfAuthorOrAdmin]

	def list(self, request, *args, **kwargs):
		queryset = self.get_object().comment_set.all()
		page = self.paginate_queryset(queryset)
		serializer = self.serializer_class(page, many=True)
		return self.paginator.get_paginated_response(serializer.data)

	def retrieve(self, request, *args, **kwargs):
		instance = self.get_object()
		serializer = self.serializer_class(instance)
		return Response({'comment': serializer.data})

	def destroy(self, request, *args, **kwargs):
		instance = self.get_object()
		self.check_object_permissions(request, instance)
		instance.delete()
		return Response({'info': f'Post is deleted'})

	def create(self, request, *args, **kwargs):
		serializer = self.serializer_class(data=request.data, context={'author': request.user})
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'created-comment': serializer.data})

	def update(self, request, *args, **kwargs):
		instance = self.get_object()
		self.check_object_permissions(request, instance)
		serializer = self.serializer_class(data=request.data, instance=instance, partial=True)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({'comment': serializer.data})


class CommentRatingAPI(RatingAPI):
	model = Comment


class UserPostsAPI(GenericAPIView):
	queryset = Post.objects.all()
	pagination_class = CustomPagination
	serializer_class = PostSerializer

	def get(self, request, *args, **kwargs):
		queryset = self.queryset.filter(author__username=kwargs.get('username'))
		page = self.paginate_queryset(queryset)
		serializer = self.serializer_class(page, many=True)
		return self.paginator.get_paginated_response(serializer.data)
