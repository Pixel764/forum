from freezegun import freeze_time
from django.test import TestCase, Client
from django.urls import reverse
from .models import Post, Comment
from users.models import CustomUserModel
from .forms import CommentForm
from users.tests import create_user


def create_post(author, title='Post title', content='Post text'):
    return Post.objects.create(title=title, content=content, author=author)


class HomePageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = CustomUserModel.objects.create_user(username='testUser')

    def test_no_posts(self):
        response = self.client.get(reverse('forum:homepage'))
        self.assertContains(response, 'There are no posts yet.')
        self.assertQuerysetEqual(response.context['posts'], [])

    def test_one_post(self):
        post = create_post(author=self.user)
        response = self.client.get(reverse('forum:homepage'))
        self.assertQuerysetEqual(response.context['posts'], [{'pk': post.pk, 'title': post.title}])

    @freeze_time('2022-01-01', auto_tick_seconds=5)
    def test_multiple_posts(self):
        post_1 = create_post(author=self.user)
        post_2 = create_post(title='Post title2', content='Post text', author=self.user)
        response = self.client.get(reverse('forum:homepage'))
        self.assertQuerysetEqual(response.context['posts'],
                                 [{'pk': post_2.pk, 'title': post_2.title}, {'pk': post_1.pk, 'title': post_1.title}])


class PostPageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.post = create_post(author=self.user)

    def test_post_exists(self):
        response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['post'], self.post)

    def test_like_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}), data={'like': ''},
                                    follow=True)
        self.assertEqual(response.context['post'].likes.count(), 1)

    def test_remove_like(self):
        self.client.force_login(self.user)
        self.post.likes.add(self.user)
        response = self.client.post(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}), data={'like': ''},
                                    follow=True)
        self.assertEqual(response.context['post'].likes.count(), 0)

    def test_create_comment(self):
        self.client.force_login(user=self.user)
        self.client.post(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}),
                         data={'text': 'comment1'})
        response = self.client.get(reverse('forum:post_page', kwargs={'post_pk': self.post.pk}))
        self.assertEqual(response.context['page_obj'].object_list[0]['text'], 'comment1')

    def test_comment_form(self):
        form = CommentForm(data={'text': 'comment text'})
        self.assertTrue(form.is_valid())


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
