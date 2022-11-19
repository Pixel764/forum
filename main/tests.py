from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time
from forum.tests import create_post

User = get_user_model()


class HomepageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username='testUser')

    def test_no_posts(self):
        response = self.client.get(reverse('main:homepage'))
        self.assertContains(response, 'There are no posts yet.')
        self.assertQuerysetEqual(response.context['posts'], [])

    def test_one_post(self):
        post = create_post(author=self.user)
        response = self.client.get(reverse('main:homepage'))
        self.assertQuerysetEqual(response.context['posts'], [{'pk': post.pk, 'title': post.title}])

    @freeze_time('2022-01-01', auto_tick_seconds=5)
    def test_multiple_posts(self):
        post_1 = create_post(author=self.user)
        post_2 = create_post(title='Post title2', content='Post text', author=self.user)
        response = self.client.get(reverse('main:homepage'))
        self.assertQuerysetEqual(response.context['posts'],
                                 [{'pk': post_2.pk, 'title': post_2.title}, {'pk': post_1.pk, 'title': post_1.title}])