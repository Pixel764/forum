from django.test import TestCase
from django.urls import reverse
from .models import Post
from .forms import CommentForm
from users.tests import create_user


def create_post(author, title='Post title', content='Post text'):
	return Post.objects.create(title=title, content=content, author=author)


class PostPageViewTest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.post = create_post(author=self.user)

	def test_post_exists(self):
		response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['post'], self.post)

	def test_create_comment(self):
		self.client.force_login(user=self.user)
		self.client.post(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}),
						 data={'text': 'comment1'})
		response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
		self.assertEqual(response.context['page_obj'].object_list[0]['text'], 'comment1')

	def test_comment_form(self):
		form = CommentForm(data={'text': 'comment text'})
		self.assertTrue(form.is_valid())


class PostRatingViewTest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.post = create_post(author=self.user)

	def test_set_like(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('forum:post_rating', kwargs={'post_pk': self.post.pk, 'status': 'like'}))
		self.assertTrue(Post.objects.get(pk=self.post.pk).likes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 1)

	def test_remove_like(self):
		self.client.force_login(self.user)
		self.post.likes.add(self.user)
		response = self.client.get(reverse('forum:post_rating', kwargs={'post_pk': self.post.pk, 'status': 'like'}))
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 0)

	def test_set_dislike(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('forum:post_rating', kwargs={'post_pk': self.post.pk, 'status': 'dislike'}))
		self.assertTrue(Post.objects.get(pk=self.post.pk).dislikes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 1)

	def test_remove_dislike(self):
		self.client.force_login(self.user)
		self.post.dislikes.add(self.user)
		response = self.client.get(reverse('forum:post_rating', kwargs={'post_pk': self.post.pk, 'status': 'dislike'}))
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 0)


class PostCreateViewTest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.client.force_login(self.user)

	def test_create_post(self):
		response = self.client.post(reverse('forum:post_create'),
									data={'title': 'Post title', 'content': 'Post text', 'author': self.user},
									follow=True)
		self.assertTrue(response.context['post'])


class PostEditViewTest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.post = create_post(author=self.user)

	def test_edit_post(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('forum:post_edit', kwargs={'post_pk': self.post.pk}),
									data={'title': 'New title'}, follow=True)
		self.assertEqual(response.context['post'].title, 'New title')

	def test_user_not_author_of_post(self):
		response = self.client.post(reverse('forum:post_edit', kwargs={'post_pk': self.post.pk}),
									data={'text': 'New Title'})
		self.assertEqual(response.status_code, 404)


class PostDeleteViewTest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.post = create_post(author=self.user)

	def test_delete_post(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('forum:post_delete', kwargs={'post_pk': self.post.pk}), follow=True)
		self.assertContains(response, 'Post was successfully deleted')

	def test_user_not_author_of_post(self):
		response = self.client.post(reverse('forum:post_delete', kwargs={'post_pk': self.post.pk}))
		self.assertEqual(response.status_code, 404)
