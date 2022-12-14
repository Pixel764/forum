from django.test import TestCase
from django.urls import reverse
from .models import Post, Category, Comment
from users.tests import create_user


def create_category(title):
    return Category.objects.create(title=title)


def create_post(author, category=None, title='Post title', content='Post text'):
    if category is None:
        category = create_category('Category1')
    return Post.objects.create(title=title, content=content, author=author, category=category)


def create_comment(author, post, text='CommentText'):
    return Comment.objects.create(author=author, post=post, text=text)


class PostPageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(author=self.user)

    def test_post_exists(self):
        response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)

    def test_create_comment(self):
        self.client.force_login(self.user)
        self.client.post(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}),
                         data={'text': 'comment1'})
        response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.context['page_obj'].object_list[0].text, 'comment1')


class PostCreateViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.category = create_category('Category1')
        self.client.force_login(self.user)

    def test_create_post(self):
        response = self.client.post(
            reverse('forum:post_create'),
            data={'title': 'Post title', 'content': 'Post text', 'author': self.user,
                  'category': f'{self.category.pk}'},
            follow=True
        )
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
        self.assertEqual(response.status_code, 403)


class PostDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(author=self.user)

    def test_delete_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('forum:post_delete', kwargs={'post_pk': self.post.pk}), follow=True)
        self.assertFalse(Post.objects.filter(pk=self.post.pk))

    def test_user_not_author_of_post(self):
        response = self.client.post(reverse('forum:post_delete', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 403)


class CommentEditViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(author=self.user)
        self.comment = create_comment(self.user, self.post)

    def test_edit_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('forum:comment_edit', kwargs={'comment_pk': self.comment.pk}),
            data={'text': 'New comment text'}, follow=True
        )
        self.assertEqual(Comment.objects.get(pk=self.comment.pk).text, 'New comment text')

    def test_user_is_not_comment_author(self):
        response = self.client.post(
            reverse('forum:comment_edit', kwargs={'comment_pk': self.comment.pk}),
            data={'text': 'New comment text'}, follow=True
        )
        self.assertEqual(response.status_code, 403)


class CommentDeleteViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(author=self.user)
        self.comment = create_comment(self.user, self.post)

    def test_delete_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('forum:comment_delete', kwargs={'comment_pk': self.comment.pk}))
        self.assertFalse(Comment.objects.filter(pk=self.comment.pk))

    def test_user_is_not_comment_author(self):
        response = self.client.post(reverse('forum:comment_delete', kwargs={'comment_pk': self.comment.pk}),)
        self.assertEqual(response.status_code, 403)


class CategoryPostsViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.category1 = create_category('Category1')
        self.category2 = create_category('Category2')
        self.post1 = create_post(author=self.user, category=self.category1)
        self.post2 = create_post(author=self.user, category=self.category2, title='Post title2')

    def test_categories_posts(self):
        response_category_1 = self.client.get(
            reverse('forum:category_posts', kwargs={'category_title': self.category1.title})
        )
        response_category_2 = self.client.get(
            reverse('forum:category_posts', kwargs={'category_title': self.category2.title})
        )
        self.assertQuerysetEqual(
            response_category_1.context['posts'], [{'title': self.post1.title, 'pk': self.post1.pk}]
        )
        self.assertQuerysetEqual(
            response_category_2.context['posts'], [{'title': self.post2.title, 'pk': self.post2.pk}]
        )
