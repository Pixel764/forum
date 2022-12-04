import freezegun
from django.test import TestCase
from django.urls import reverse
import json
from users.tests import create_user
from forum.tests import create_post
from forum.models import Post


def bytes_to_dict(content: bytes):
	return json.loads(content.decode('utf-8'))


class PostCRUDAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()

	def test_all_posts(self):
		create_post(self.user)
		create_post(self.user)
		response = self.client.get(reverse('api:all_posts'))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 2)

	def test_amount_posts(self):
		create_post(self.user)
		create_post(self.user)
		response = self.client.get(reverse('api:amount_posts', kwargs={'amount': 1}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 1)

	def test_get_post(self):
		post = create_post(self.user)
		response = self.client.get(reverse('api:get_edit_delete_post', kwargs={'pk': post.pk}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('post' in response_content_in_dict)

	def test_edit_post(self):
		self.client.force_login(self.user)
		post = create_post(self.user)
		data = {
			'title': 'New title'
		}
		response = self.client.put(
			reverse('api:get_edit_delete_post', kwargs={'pk': post.pk}), data=data, content_type='application/json'
		)
		self.assertEqual(Post.objects.get(pk=post.pk).title, 'New title')

	def test_delete_post(self):
		self.client.force_login(self.user)
		post = create_post(self.user)
		response = self.client.delete(reverse('api:get_edit_delete_post', kwargs={'pk': post.pk}))
		self.assertFalse(Post.objects.all())

	def test_create_post(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse('api:create_post'), data={'title': 'New post', 'content': 'Post content'}, follow=True
		)
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('created-post' in response_content_in_dict)


class PostRatingAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.post = create_post(author=self.user)

	def test_set_like(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Post.objects.get(pk=self.post.pk).likes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 1)
		self.assertEqual(response_content_in_dict['likes'], 1)

	def test_remove_like(self):
		self.client.force_login(self.user)
		self.post.likes.add(self.user)
		response = self.client.get(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 0)
		self.assertEqual(response_content_in_dict['likes'], 0)

	def test_set_dislike(self):
		self.client.force_login(self.user)
		response = self.client.get(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Post.objects.get(pk=self.post.pk).dislikes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 1)
		self.assertEqual(response_content_in_dict['dislikes'], 1)

	def test_remove_dislike(self):
		self.client.force_login(self.user)
		self.post.dislikes.add(self.user)
		response = self.client.get(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 0)
		self.assertEqual(response_content_in_dict['dislikes'], 0)


class UserPostsAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()

	@freezegun.freeze_time('2021-01-01')
	def test_user_posts(self):
		create_post(self.user)
		create_post(self.user)
		response = self.client.get(reverse('api:user_posts', kwargs={'username': self.user.username}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 2)

	def test_user_amount_posts(self):
		create_post(self.user)
		create_post(self.user)
		response = self.client.get(
			reverse('api:user_amount_posts', kwargs={'username': self.user.username, 'amount': 1})
		)
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 1)
