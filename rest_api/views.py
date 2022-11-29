from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import UpdateIfAuthorOrAdmin
from forum.models import Post
from .serializers import PostSerializer
from .pagination import PostPagination
from rest_framework.generics import GenericAPIView


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


# User api views
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
