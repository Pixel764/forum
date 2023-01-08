from django.shortcuts import get_object_or_404, render
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


# Http handlers views
def http400(request, exception):
    return render(request, 'http/400.html', status=400)


def http403(request, exception):
    return render(request, 'http/403.html', status=403)


def http404(request, exception):
    return render(request, 'http/404.html', status=404)


def http500(request):
    return render(request, 'http/500.html', status=500)
