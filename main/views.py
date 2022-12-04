from django.utils import timezone
from forum.models import Post
from django.views.generic import ListView


class HomepageView(ListView):
	model = Post
	template_name = 'index.html'
	context_object_name = 'posts'
	paginate_by = 30

	def get_queryset(self):
		return Post.objects.filter(published_date__lte=timezone.now()).values('title', 'pk')


class SearchView(ListView):
	model = Post
	template_name = 'index.html'
	context_object_name = 'posts'
	paginate_by = 30

	def get_queryset(self):
		return Post.objects.filter(
			title__icontains=self.request.GET['q'], published_date__lte=timezone.now()
		).values('title', 'pk')
