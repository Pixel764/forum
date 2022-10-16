import os

from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import EmailCode
from .tasks import send_email

site = Site.objects.get_current()


class EmailConfirmationCode:
    def send_email_code(self, email):
        context = self.get_email_context(email)
        send_email.delay(
            'Code for email confirmation',
            'users/email/email_change_email.html',
            email,
            context
        )

    def get_email_context(self, email):
        context = {
            'site_name': site.name,
            'code': self.get_code(email),
        }
        return context

    def get_code(self, email):
        # Create a email confirmation code
        try:
            code = EmailCode.objects.get(email=email)
        except ObjectDoesNotExist:
            pass
        else:
            code.delete()

        code = EmailCode.objects.create(email=email).code
        return code


def delete_profile_image(user):
    user_profile_image_path = str(settings.MEDIA_ROOT) + '/' + user.profile_image.name
    try:
        os.remove(user_profile_image_path)
    except FileNotFoundError:
        pass
