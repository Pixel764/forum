from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, CreateView, DeleteView, UpdateView
from django.views.generic.edit import FormMixin
from .models import Post, Comment
from .forms import CreateAndEditPostForm, CommentForm
from django.contrib import messages


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
			self.object.comment_set.values('author__username', 'author__id', 'pk', 'text', 'published_date'),
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


@login_required()
def post_rating_view(request, post_pk, status):
	accepted_status = ['like', 'dislike']

	if status not in accepted_status:
		raise Http404

	try:
		post = Post.objects.get(pk=post_pk)
	except ObjectDoesNotExist:
		return JsonResponse({'error': 'Post not found'})

	if status == 'like':
		set_like(post, request.user)
	else:
		set_dislike(post, request.user)

	return JsonResponse({'likes': post.likes.count(), 'dislikes': post.dislikes.count()})


def set_like(post, user):
	if post.likes.filter(pk=user.pk):
		post.likes.remove(user)
	else:
		if post.dislikes.filter(pk=user.pk):
			post.dislikes.remove(user)
		post.likes.add(user)


def set_dislike(post, user):
	if post.dislikes.filter(pk=user.pk):
		post.dislikes.remove(user)
	else:
		if post.likes.filter(pk=user.pk):
			post.likes.remove(user)
		post.dislikes.add(user)


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
			raise Http404

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
			raise Http404

	def form_valid(self, form):
		messages.add_message(self.request, messages.SUCCESS, 'Post was successfully deleted')
		return super(PostDeleteView, self).form_valid(form)


@method_decorator(require_POST, name='dispatch')
class CommentDeleteView(DeleteView):
	model = Comment
	pk_url_kwarg = 'comment_pk'

	def dispatch(self, request, *args, **kwargs):
		if self.get_object().author == self.request.user:
			return super(CommentDeleteView, self).post(request, *args, **kwargs)
		else:
			raise Http404

	def form_valid(self, form):
		self.object.delete()
		messages.add_message(self.request, messages.SUCCESS, 'Comment was successfully deleted')
		return HttpResponseRedirect(self.object.get_absolute_url())
