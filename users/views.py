from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, DetailView, UpdateView, FormView, TemplateView
from forum_app.models import Post
from .forms import SignUpForm, ChangeEmailForm, LoginForm, ProfileVerificationForm, CustomPasswordResetForm
from django.contrib.auth import views as auth_views
from django.contrib.auth import login, get_user_model
from .forms import EditProfileForm, EmailCodeCheckForm
from .models import CustomUserModel, EmailCode
from .utils import delete_profile_image
from .utils import EmailConfirmationCode
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator


class SignUpView(EmailConfirmationCode, CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('users:email_confirm', kwargs={'status': 'confirm'})
    template_name = 'users/registration/signup.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('forum:homepage'))
        else:
            return super(SignUpView, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        self.send_email_code(self.object.email)
        return HttpResponseRedirect(self.get_success_url())


class AuthenticationView(auth_views.LoginView):
    form_class = LoginForm
    template_name = 'users/registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('forum:homepage'))
        else:
            return super(AuthenticationView, self).dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
class ConfirmEmailView(EmailConfirmationCode, FormView):
    form_class = EmailCodeCheckForm
    success_url = reverse_lazy('forum:homepage')
    template_name = 'users/registration/email_confirm_form.html'
    status_names = ['send', 'confirm']

    def dispatch(self, request, *args, **kwargs):
        if self.kwargs['status'] in self.status_names:
            if self.request.user.email_confirmed:
                return HttpResponseRedirect(reverse('forum:homepage'))
            elif self.kwargs['status'] == 'send':
                self.send_email_code(self.request.user.email)
                return HttpResponseRedirect(reverse('users:email_confirm', kwargs={'status': 'confirm'}))
            else:
                if not EmailCode.objects.filter(email=self.request.user.email):
                    return HttpResponseRedirect(reverse('users:email_confirm', kwargs={'status': 'send'}))
                else:
                    return super(ConfirmEmailView, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404

    def get_form_kwargs(self):
        kwargs = super(ConfirmEmailView, self).get_form_kwargs()
        kwargs['verification_code'] = EmailCode.objects.get(email=self.request.user.email).code
        return kwargs

    def form_valid(self, form):
        self.request.user.email_confirmed = True
        self.request.user.save()
        EmailCode.objects.get(email=self.request.user.email).delete()
        return super(ConfirmEmailView, self).form_valid(form)


# Profile views
class ProfileView(DetailView):
    model = CustomUserModel
    template_name = 'users/profile.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'

    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        context['title'] = self.request.user.username
        context['paginator'] = Paginator(self.object.post_set.values('pk', 'title'),
                                         self.paginate_by)
        context['page_obj'] = self.get_page_obj(context['paginator'], self.request.GET.get('page'))
        return context

    def get_page_obj(self, paginator, page_number):
        if page_number is None:
            page_number = 1
        page_obj = paginator.page(page_number)
        return page_obj


class ProfileEditView(UpdateView):
    template_name = 'users/profile_edit.html'
    form_class = EditProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super(ProfileEditView, self).get_context_data(**kwargs)
        context['title'] = 'Profile Settings'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        if 'profile_image' in form.changed_data:
            delete_profile_image(self.request.user)
        return super(ProfileEditView, self).form_valid(form)


# Reset password views
class CustomPasswordResetView(FormView):
    template_name = 'users/password/password_reset/password_reset_form.html'
    message_template = 'users/password/password_reset/password_reset_email.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')
    token_generator = default_token_generator

    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.post(request, *args, **kwargs, email=self.request.user.email)
        else:
            return super(CustomPasswordResetView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if 'email' in kwargs:
            form = self.form_class(data={'email': kwargs['email']})
        else:
            form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        site = get_current_site(self.request)
        opts = {
            'subject': f'Password reset on {site.name}',
            'message_template': self.message_template,
            'request': self.request,
            'token_generator': self.token_generator
        }
        form.save(**opts)
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password/password_reset/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password/password_reset/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password/password_reset/password_reset_complete.html'


# Change password views
class CustomPasswordChangeView(auth_views.PasswordChangeView):
    success_url = reverse_lazy('users:password_change_done')
    template_name = 'users/password/password_change/password_change_form.html'


class CustomPasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = 'users/password/password_change/password_change_done.html'


# Change email
@method_decorator(login_required, name='dispatch')
class ChangeEmailView(FormView):
    template_name = 'users/email/profile_verification.html'
    form_class = ProfileVerificationForm
    success_url = reverse_lazy('users:email_change_confirm')

    def get_form_kwargs(self):
        kwargs = super(ChangeEmailView, self).get_form_kwargs()
        kwargs['user_password'] = self.request.user.password
        return kwargs

    def form_valid(self, form):
        self.request.session['access_change_email'] = True
        return super(ChangeEmailView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ChangeEmailConfirmView(EmailConfirmationCode, FormView):
    template_name = 'users/email/email_change_form.html'
    form_class = ChangeEmailForm
    success_url = reverse_lazy('users:email_change_confirm_new_email', kwargs={'status': 'confirm'})

    def dispatch(self, request, *args, **kwargs):
        if 'access_change_email' in self.request.session.keys() and self.request.session['access_change_email']:
            return super(ChangeEmailConfirmView, self).dispatch(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('users:email_change_verification'))

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            self.request.session['new_email'] = form.cleaned_data['new_email']
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        self.send_email_code(self.request.session['new_email'])
        return super(ChangeEmailConfirmView, self).form_valid(form)


@method_decorator(login_required, name='dispatch')
class ConfirmNewEmailView(EmailConfirmationCode, FormView):
    template_name = 'users/email/email_change_confirm.html'
    form_class = EmailCodeCheckForm
    success_url = reverse_lazy('users:profile_edit')
    status_names = ['send', 'confirm']

    def dispatch(self, request, *args, **kwargs):
        if 'new_email' not in self.request.session.keys():
            return HttpResponseRedirect(reverse('users:email_change_verification'))
        else:
            if self.kwargs['status'] in self.status_names:
                if self.kwargs['status'] == 'send':
                    self.send_email_code(self.request.session['new_email'])
                    return HttpResponseRedirect(
                        reverse('users:email_change_confirm_new_email', kwargs={'status': 'confirm'}))
                else:
                    if not EmailCode.objects.filter(email=self.request.session['new_email']):
                        return HttpResponseRedirect(
                            reverse('users:email_change_confirm_new_email', kwargs={'status': 'send'}))
                    else:
                        return super(ConfirmNewEmailView, self).dispatch(request, *args, **kwargs)
            else:
                raise Http404

    def get_form_kwargs(self):
        kwargs = super(ConfirmNewEmailView, self).get_form_kwargs()
        kwargs['verification_code'] = EmailCode.objects.get(email=self.request.session['new_email']).code
        return kwargs

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            self.request.user.email = self.request.session['new_email']
            self.request.user.save()
            del self.request.session['new_email']
            EmailCode.objects.get(email=self.request.user.email).delete()
            messages.add_message(self.request, messages.SUCCESS, 'Email successfully changed.')
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
