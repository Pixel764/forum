from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from captcha.fields import CaptchaField
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from .models import CustomUserModel, EmailCode
from .tasks import send_email

UserModel = get_user_model()


# Registration forms
class LoginForm(AuthenticationForm):
    captcha = CaptchaField()

    class Meta:
        model = CustomUserModel
        fields = ['username']

    error_messages = {
        'invalid_login':
            'Please enter a correct %(username)s and password'
        ,
        'inactive': 'This account is inactive',
    }


class SignUpForm(UserCreationForm):
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    captcha = CaptchaField()

    class Meta:
        model = CustomUserModel
        fields = ['username', 'email']


# Profile forms
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUserModel
        fields = ['username', 'profile_image', 'email']

        widgets = {
            'email': forms.EmailInput(attrs={'readonly': True}),
        }

    def clean_profile_image(self):
        img = self.cleaned_data['profile_image']
        img_name, img_suffix = self.cleaned_data['profile_image'].name.split('.')
        img.name = f'{img_name}.jpg'
        return img


class ProfileVerificationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user_password = kwargs.pop('user_password')
        super(ProfileVerificationForm, self).__init__(*args, **kwargs)

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def clean_password(self):
        password = self.cleaned_data['password']
        if check_password(password, self.user_password):
            return password
        else:
            raise ValidationError('Incorrect password')


# Email verification forms
class EmailCodeCheckForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.verification_code = kwargs.pop('verification_code')
        super(EmailCodeCheckForm, self).__init__(*args, **kwargs)

    code = forms.IntegerField(widget=forms.TextInput(attrs={'maxlength': 6}))

    def clean_code(self):
        code = self.cleaned_data['code']
        if code != self.verification_code:
            raise ValidationError('Incorrect code')
        else:
            return code


class ChangeEmailForm(forms.Form):
    new_email = forms.EmailField(widget=forms.EmailInput())

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email']
        if CustomUserModel.objects.filter(email=new_email).exists():
            raise ValidationError('User with this email already exist')
        else:
            return new_email


# Password forms
class CustomPasswordResetForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        max_length=254,
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )

    def send_mail(self, subject, message_template, user_email, context):
        send_email.delay(subject, message_template, user_email, context)

    def get_user(self, email):
        try:
            user = UserModel.objects.get(email=email, is_active=True)
        except ObjectDoesNotExist:
            raise ValidationError('User not found')
        else:
            return user

    def save(
            self,
            subject,
            message_template,
            request,
            use_https=False,
            token_generator=default_token_generator,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"]
        current_site = get_current_site(request)
        user = self.get_user(email)
        context = {
            'protocol': 'https' if use_https else 'http',
            'domain': current_site.domain,
            'site_name': current_site.name,
            'email': user.email,
            'username': user.username,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
        }
        self.send_mail(subject, message_template, user.email, context)


# Admin panel forms
class AdminPanelEditProfileForm(UserChangeForm):
    class Meta:
        model = CustomUserModel
        fields = ['username', 'email']
