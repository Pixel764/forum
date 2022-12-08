from .models import Category


class CategoryContextMixin:
	def get_category_context(self, **kwargs):
		context = kwargs
		context['categories'] = Category.objects.all()

		if 'selected_category' not in context:
			context['selected_category'] = None

		return context
