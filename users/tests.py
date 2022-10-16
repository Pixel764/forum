from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from .models import CustomUserModel, EmailCode
from captcha.conf import settings as captcha_conf
from forum.celery import app


def create_user(username='testUser', email='test@gmail.com', password='password123', email_confirmed=True):
    user = CustomUserModel.objects.create(username=username, email=email, email_confirmed=email_confirmed)
    user.password = make_password(password)
    user.save()
    return user


class SignUpViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        captcha_conf.CAPTCHA_TEST_MODE = True

    def test_signup(self):
        data = {
            'username': 'testUser',
            'email': 'test@gmail.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
            'captcha_0': 'PASSED',
            'captcha_1': 'PASSED'
        }
        response = self.client.post(reverse('users:signup'), data=data, follow=True)
        celery_app = app.control.inspect()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(celery_app.active()), 1)
        self.assertTrue(CustomUserModel.objects.filter(email=data['email']))


class LoginViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        captcha_conf.CAPTCHA_TEST_MODE = True

    def setUp(self) -> None:
        self.user = create_user(password='password123')

    def test_successfully_login(self):
        data = {
            'username': 'testUser',
            'password': 'password123',
            'captcha_0': 'PASSED',
            'captcha_1': 'PASSED',
        }
        response = self.client.post(reverse('users:login'), data=data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].username, self.user.username)


class ConfirmEmailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user(email_confirmed=False)

    def test_successfully_email_confirm(self):
        self.client.force_login(self.user)
        make_code_request = self.client.get(reverse('users:email_confirm', kwargs={'status': 'send'}))
        data = {
            'code': EmailCode.objects.get(email=self.user.email)
        }
        confirm_email_request = self.client.post(
            reverse('users:email_confirm', kwargs={'status': 'confirm'}), data=data, follow=True)
        self.assertTrue(confirm_email_request.context['user'].email_confirmed)

    def test_invalid_email_code(self):
        self.client.force_login(self.user)
        make_code_request = self.client.get(reverse('users:email_confirm', kwargs={'status': 'send'}))
        response = self.client.post(reverse('users:email_confirm', kwargs={'status': 'confirm'}),
                                    data={'code': '000000'}, follow=True)
        self.assertContains(response, 'Incorrect code')


class ProfileViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_profile_found(self):
        response = self.client.get(reverse('users:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.user)

    def test_profile_doesnt_exist(self):
        response = self.client.get(reverse('users:profile', kwargs={'username': 'username123'}))
        self.assertEqual(response.status_code, 404)


class ProfileEditViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_change_username(self):
        self.client.force_login(self.user)
        data = {
            'username': 'NewUsername',
            'email': self.user.email
        }
        response = self.client.post(reverse('users:profile_edit'), data=data, follow=True)
        self.assertEqual(response.context['user'].username, 'NewUsername')

    def test_username_already_exist(self):
        user_2 = create_user(username='testUser2', email='test2@gmail.com')
        self.client.force_login(self.user)
        data = {
            'username': 'testUser2',
            'email': self.user.email
        }
        response = self.client.post(reverse('users:profile_edit'), data=data, follow=True)
        self.assertContains(response, 'A user with that username already exists.')


class PasswordResetViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_user_is_not_logged(self):
        # if user is not logged he need to enter email
        response = self.client.get(reverse('users:password_reset'), follow=True)
        self.assertFalse(response.redirect_chain)

    def test_user_is_logged(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('users:password_reset'), follow=True)
        celery_app = app.control.inspect()
        self.assertEqual(len(celery_app.active()), 1)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Check your email')


class ChangeEmailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()

    def test_user_has_passed_verification(self):
        self.client.force_login(self.user)
        data = {
            'password': 'password123'
        }
        response = self.client.post(reverse('users:email_change_verification'), data=data, follow=True)
        self.assertEqual(response.redirect_chain[0][0], reverse('users:email_change_confirm'))


class ChangeEmailConfirmViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        session = self.client.session
        session.update({
            'access_change_email': True
        })
        session.save()

    def test_new_email_is_available(self):
        self.client.force_login(self.user)
        data = {
            'new_email': 'newemail@gmail.com'
        }
        response = self.client.post(reverse('users:email_change_confirm'), data=data, follow=True)
        celery_app = app.control.inspect()
        self.assertTrue(list(celery_app.active().values())[0])
        self.assertEqual(response.redirect_chain[0][0],
                         reverse('users:email_change_confirm_new_email', kwargs={'status': 'confirm'}))

    def test_new_email_is_not_available(self):
        create_user(username='testUser2', email='newemail@gmail.com')
        self.client.force_login(self.user)
        data = {
            'new_email': 'newemail@gmail.com'
        }
        response = self.client.post(reverse('users:email_change_confirm'), data=data, follow=True)
        celery_app = app.control.inspect()
        self.assertFalse(list(celery_app.active().values())[0])
        self.assertContains(response, 'User with this email already exist')


class ConfirmNewEmailViewTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user()
        session = self.client.session
        session.update({
            'new_email': 'newemail@gmail.com'
        })
        session.save()
        self.code = EmailCode.objects.create(email='newemail@gmail.com').code

    def test_enter_valid_verification_code(self):
        self.client.force_login(self.user)
        data = {
            'code': self.code
        }
        response = self.client.post(reverse('users:email_change_confirm_new_email', kwargs={'status': 'confirm'}),
                                    data=data, follow=True)
        self.assertTrue(response.context['messages'])
        self.assertTrue('new_email' not in response.context['request'].session.keys())
        self.assertEqual(response.context['user'].email, 'newemail@gmail.com')

    def test_enter_invalid_verification_code(self):
        self.client.force_login(self.user)
        data = {
            'code': '000000'
        }
        response = self.client.post(reverse('users:email_change_confirm_new_email', kwargs={'status': 'confirm'}),
                                    data=data, follow=True)
        self.assertContains(response, 'Incorrect code')
        self.assertEqual(response.context['user'].email, self.user.email)
