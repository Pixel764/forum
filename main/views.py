from django.shortcuts import get_object_or_404
from django.utils import timezone
from forum.models import Post, Category
from django.views.generic import ListView
from forum.utils import CategoryContextMixin


class HomepageView(CategoryContextMixin, ListView):
	model = Post
	template_name = 'index.html'
	context_object_name = 'posts'
	paginate_by = 30

	def get_queryset(self):
		return Post.objects.filter(published_date__lte=timezone.now()).values('title', 'pk')

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super(HomepageView, self).get_context_data(**kwargs)
		category_context = self.get_category_context()
		context = dict(list(context.items()) + list(category_context.items()))
		return context


class SearchView(CategoryContextMixin, ListView):
	model = Post
	template_name = 'index.html'
	context_object_name = 'posts'
	paginate_by = 30

	def get_queryset(self):
		queryset = Post.objects.filter(
			title__icontains=self.request.GET['q'], published_date__lte=timezone.now()
		).values('title', 'pk')

		if 'category_title' in self.kwargs:
			queryset = queryset.filter(category__title=self.kwargs['category_title'])

		return queryset

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super(SearchView, self).get_context_data(**kwargs)
		category_context = self.get_category_context()

		if 'category_title' in self.kwargs:
			category_context['selected_category'] = get_object_or_404(Category, title=self.kwargs['category_title'])

		context = dict(list(context.items()) + list(category_context.items()))
		return context
