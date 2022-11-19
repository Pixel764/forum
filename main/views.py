from forum.models import Post
from django.views.generic import ListView


class HomepageView(ListView):
	model = Post
	template_name = 'index.html'
	context_object_name = 'posts'
	paginate_by = 30

	def get_queryset(self):
		return Post.objects.all().values('title', 'pk')
