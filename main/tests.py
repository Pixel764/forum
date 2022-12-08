from forum.tests import create_category
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time
from forum.tests import create_post
from users.tests import create_user


class HomepageViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.category = create_category('Category1')

    def test_no_posts(self):
        response = self.client.get(reverse('main:homepage'))
        self.assertContains(response, 'There are no posts yet.')
        self.assertQuerysetEqual(response.context['posts'], [])

    def test_one_post(self):
        post = create_post(author=self.user, category=self.category)
        response = self.client.get(reverse('main:homepage'))
        self.assertQuerysetEqual(response.context['posts'], [{'pk': post.pk, 'title': post.title}])

    @freeze_time('2022-01-01', auto_tick_seconds=5)
    def test_multiple_posts(self):
        post_1 = create_post(author=self.user, category=self.category)
        post_2 = create_post(title='Post title2', content='Post text', author=self.user, category=self.category)
        response = self.client.get(reverse('main:homepage'))
        self.assertQuerysetEqual(response.context['posts'],
                                 [{'pk': post_2.pk, 'title': post_2.title}, {'pk': post_1.pk, 'title': post_1.title}])


class SearchViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        self.category = create_category('Category1')

    def test_search_without_category(self):
        create_post(author=self.user, category=self.category)
        post = create_post(author=self.user, category=self.category, title='Post2')
        response = self.client.get(reverse('main:search_posts'), data={'q': 'st2'})
        self.assertQuerysetEqual(response.context['posts'], [{'title': 'Post2', 'pk': post.pk}])

    def test_search_with_category(self):
        category2 = create_category('Category2')
        post1 = create_post(author=self.user, category=self.category, title='Test1')
        post2 = create_post(author=self.user, category=category2, title='Post2')
        post3 = create_post(author=self.user, category=category2, title='Test2')
        response = self.client.get(
            reverse('main:search_category_posts', kwargs={'category_title': category2.title}), data={'q': 'Test'}
        )
        self.assertQuerysetEqual(response.context['posts'], [{'title': post3.title, 'pk': post3.pk}])
