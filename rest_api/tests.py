import freezegun
from django.test import TestCase
from django.urls import reverse
import json
from users.tests import create_user
from forum.tests import create_post, create_category, create_comment
from forum.models import Post, Comment


def bytes_to_dict(content: bytes):
	return json.loads(content.decode('utf-8'))


class CategoryAPITest(TestCase):
	def setUp(self) -> None:
		self.author = create_user()
		self.category1 = create_category('Category1')
		self.category2 = create_category('Category2')
		self.post = create_post(author=self.author, category=self.category2)

	def test_categories_list(self):
		response = self.client.get((reverse('api:categories_list')))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 2)

	def test_category_posts(self):
		response1 = self.client.get(reverse('api:category_posts', kwargs={'pk': self.category1.pk}))
		response2 = self.client.get(reverse('api:category_posts', kwargs={'pk': self.category2.pk}))
		response_content_in_dict1 = bytes_to_dict(response2.content)
		response_content_in_dict2 = bytes_to_dict(response2.content)
		self.assertEqual(response_content_in_dict1['count'], 1)
		self.assertEqual(response_content_in_dict2['count'], 1)


class PostAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.category = create_category('Category1')

	def test_all_posts(self):
		create_post(self.user, category=self.category)
		create_post(self.user, category=self.category)
		response = self.client.get(reverse('api:posts_all'))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 2)

	def test_get_post(self):
		post = create_post(self.user, category=self.category)
		response = self.client.get(reverse('api:post_get_edit_delete', kwargs={'pk': post.pk}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('post' in response_content_in_dict)

	def test_edit_post(self):
		self.client.force_login(self.user)
		post = create_post(self.user, category=self.category)
		data = {
			'title': 'New title'
		}
		response = self.client.put(
			reverse('api:post_get_edit_delete', kwargs={'pk': post.pk}), data=data, content_type='application/json'
		)
		self.assertEqual(Post.objects.get(pk=post.pk).title, 'New title')

	def test_delete_post(self):
		self.client.force_login(self.user)
		post = create_post(self.user, category=self.category)
		response = self.client.delete(reverse('api:post_get_edit_delete', kwargs={'pk': post.pk}))
		self.assertFalse(Post.objects.all())

	def test_create_post(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse('api:post_create'),
			data={'title': 'New post', 'content': 'Post content', 'category': f'{self.category.pk}'},
			follow=True
		)
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('created-post' in response_content_in_dict)
		self.assertTrue(Post.objects.get(title='New post'))


class PostRatingAPITest(TestCase):
	def setUp(self) -> None:
		self.category = create_category('Category1')
		self.user = create_user()
		self.post = create_post(author=self.user, category=self.category)

	def test_set_like(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Post.objects.get(pk=self.post.pk).likes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 1)
		self.assertEqual(response_content_in_dict['likes'], 1)

	def test_remove_like(self):
		self.client.force_login(self.user)
		self.post.likes.add(self.user)
		response = self.client.post(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Post.objects.get(pk=self.post.pk).likes.count(), 0)
		self.assertEqual(response_content_in_dict['likes'], 0)

	def test_set_dislike(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Post.objects.get(pk=self.post.pk).dislikes.filter(pk=self.user.pk))
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 1)
		self.assertEqual(response_content_in_dict['dislikes'], 1)

	def test_remove_dislike(self):
		self.client.force_login(self.user)
		self.post.dislikes.add(self.user)
		response = self.client.post(reverse('api:post_rating', kwargs={'pk': self.post.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Post.objects.get(pk=self.post.pk).dislikes.count(), 0)
		self.assertEqual(response_content_in_dict['dislikes'], 0)


class CommentAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.category = create_category('Category1')
		self.post = create_post(self.user, self.category)

	def test_get_comment(self):
		comment = create_comment(self.user, self.post)
		response = self.client.get(reverse('api:comment_get_edit_delete', kwargs={'pk': comment.pk}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('CommentText' == response_content_in_dict['comment']['text'])

	def test_edit_comment(self):
		self.client.force_login(self.user)
		comment = create_comment(self.user, self.post)
		data = {
			'text': 'New text'
		}
		response = self.client.put(
			reverse('api:comment_get_edit_delete', kwargs={'pk': comment.pk}), data=data, content_type='application/json'
		)
		self.assertEqual(Comment.objects.get(pk=comment.pk).text, 'New text')

	def test_user_is_not_author_edit_comment(self):
		comment = create_comment(self.user, self.post)
		data = {
			'text': 'New text'
		}
		response = self.client.put(
			reverse('api:comment_get_edit_delete', kwargs={'pk': comment.pk}), data=data
		)
		self.assertEqual(response.status_code, 403)

	def test_delete_comment(self):
		self.client.force_login(self.user)
		comment = create_comment(self.user, self.post)
		response = self.client.delete(reverse('api:comment_get_edit_delete', kwargs={'pk': comment.pk}))
		self.assertFalse(Comment.objects.all())

	def test_user_is_not_author_delete_comment(self):
		comment = create_comment(self.user, self.post)
		response = self.client.delete(reverse('api:comment_get_edit_delete', kwargs={'pk': comment.pk}))
		self.assertEqual(response.status_code, 403)

	def test_create_post(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse('api:comment_create'),
			data={'text': 'New comment', 'post': f'{self.post.pk}'},
			follow=True
		)
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue('New comment' == response_content_in_dict['created-comment']['text'])
		self.assertTrue(Comment.objects.get(text='New comment'))


class CommentRatingAPITest(TestCase):
	def setUp(self) -> None:
		self.category = create_category('Category1')
		self.user = create_user()
		self.post = create_post(author=self.user, category=self.category)
		self.comment = create_comment(self.user, self.post)

	def test_set_like(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('api:comment_rating', kwargs={'pk': self.comment.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Comment.objects.get(pk=self.comment.pk).likes.filter(pk=self.user.pk))
		self.assertEqual(Comment.objects.get(pk=self.comment.pk).likes.count(), 1)
		self.assertEqual(response_content_in_dict['likes'], 1)

	def test_remove_like(self):
		self.client.force_login(self.user)
		self.comment.likes.add(self.user)
		response = self.client.post(reverse('api:comment_rating', kwargs={'pk': self.comment.pk, 'status': 'like'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Comment.objects.get(pk=self.comment.pk).likes.count(), 0)
		self.assertEqual(response_content_in_dict['likes'], 0)

	def test_set_dislike(self):
		self.client.force_login(self.user)
		response = self.client.post(reverse('api:comment_rating', kwargs={'pk': self.comment.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertTrue(Comment.objects.get(pk=self.comment.pk).dislikes.filter(pk=self.user.pk))
		self.assertEqual(Comment.objects.get(pk=self.comment.pk).dislikes.count(), 1)
		self.assertEqual(response_content_in_dict['dislikes'], 1)

	def test_remove_dislike(self):
		self.client.force_login(self.user)
		self.comment.dislikes.add(self.user)
		response = self.client.post(reverse('api:comment_rating', kwargs={'pk': self.comment.pk, 'status': 'dislike'}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(Comment.objects.get(pk=self.comment.pk).dislikes.count(), 0)
		self.assertEqual(response_content_in_dict['dislikes'], 0)


class UserPostsAPITest(TestCase):
	def setUp(self) -> None:
		self.user = create_user()
		self.category = create_category('Category1')

	@freezegun.freeze_time('2021-01-01')
	def test_user_posts(self):
		create_post(self.user, category=self.category)
		create_post(self.user, category=self.category)
		response = self.client.get(reverse('api:user_posts', kwargs={'username': self.user.username}))
		response_content_in_dict = bytes_to_dict(response.content)
		self.assertEqual(response_content_in_dict['count'], 2)
