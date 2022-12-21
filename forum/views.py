from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView, ListView
from django.views.generic.edit import FormMixin
from .models import Post, Comment, Category
from .forms import CreateAndEditPostForm, CommentForm
from django.contrib import messages
from .utils import CategoryContextMixin


@method_decorator(login_required, name='post')
class PostPageView(FormMixin, DetailView):
	model = Post
	template_name = 'forum/post_page.html'
	form_class = CommentForm
	pk_url_kwarg = 'post_pk'
	paginate_by = 30

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def get_context_data(self, **kwargs):
		context = super(PostPageView, self).get_context_data(**kwargs)
		context['paginator'] = Paginator(
			self.object.comment_set.all().select_related('author').prefetch_related('likes', 'dislikes'),
			self.paginate_by
		)
		context['page_obj'] = self.get_page_obj(context['paginator'], self.request.GET.get('page', 1))
		return context

	def get_page_obj(self, paginator, page_number):
		page_obj = paginator.page(page_number)
		return page_obj

	def form_valid(self, form):
		form.instance.post = self.object
		form.instance.author = self.request.user
		form.save()
		return HttpResponseRedirect(self.object.get_absolute_url())


@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
	template_name = 'forum/post_create_and_edit.html'
	form_class = CreateAndEditPostForm

	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)

	def form_valid(self, form):
		form.instance.author = self.request.user
		return super(PostCreateView, self).form_valid(form)


class PostEditView(UpdateView):
	model = Post
	template_name = 'forum/post_create_and_edit.html'
	form_class = CreateAndEditPostForm
	pk_url_kwarg = 'post_pk'

	def dispatch(self, request, *args, **kwargs):
		if self.get_object().author == self.request.user:
			return super(PostEditView, self).dispatch(request, *args, **kwargs)
		else:
			raise PermissionDenied

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		form = self.get_form()

		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)


@method_decorator(require_POST, name='dispatch')
class PostDeleteView(DeleteView):
	model = Post
	pk_url_kwarg = 'post_pk'
	success_url = reverse_lazy('main:homepage')

	def dispatch(self, request, *args, **kwargs):
		if self.get_object().author == self.request.user:
			return super(PostDeleteView, self).post(request, *args, **kwargs)
		else:
			raise PermissionDenied

	def form_valid(self, form):
		messages.add_message(self.request, messages.SUCCESS, 'Post was successfully deleted')
		return super(PostDeleteView, self).form_valid(form)


class CommentEditView(UpdateView):
	model = Comment
	template_name = 'forum/comment_edit.html'
	form_class = CommentForm
	pk_url_kwarg = 'comment_pk'

	def dispatch(self, request, *args, **kwargs):
		if self.get_object().author == self.request.user:
			return super(CommentEditView, self).dispatch(request, *args, **kwargs)
		else:
			raise PermissionDenied

	def form_valid(self, form):
		form.save()
		return HttpResponseRedirect(self.object.get_absolute_url())


@method_decorator(require_POST, name='dispatch')
class CommentDeleteView(DeleteView):
	model = Comment
	pk_url_kwarg = 'comment_pk'

	def dispatch(self, request, *args, **kwargs):
		if self.get_object().author == self.request.user:
			return super(CommentDeleteView, self).post(request, *args, **kwargs)
		else:
			raise PermissionDenied

	def form_valid(self, form):
		self.object.delete()
		messages.add_message(self.request, messages.SUCCESS, 'Comment was successfully deleted')
		return HttpResponseRedirect(self.object.get_absolute_url())


class CategoryPostsView(CategoryContextMixin, ListView):
	context_object_name = 'posts'
	template_name = 'index.html'
	paginate_by = 30

	def get_queryset(self):
		return Post.objects.filter(
			category__title=self.kwargs['category_title'], published_date__lte=timezone.now()
		).values('title', 'pk')

	def get_context_data(self, *, object_list=None, **kwargs):
		context = super(CategoryPostsView, self).get_context_data(**kwargs)
		category_context = self.get_category_context(selected_category=get_object_or_404(Category, title=self.kwargs['category_title']))
		context = dict(list(context.items()) + list(category_context.items()))
		return context
