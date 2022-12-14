from .models import EmailCode
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from .tasks import send_email

# Block exception "table not found" when make migration for first time
try:
    site = Site.objects.get_current()
except:
    print('Do migrations! python manage.py migrate')

userModel = get_user_model()


class EmailConfirmationCode:
    """ generating and submitting email code """

    def send_email_code(self, email: str):
        context = self.__get_email_context(email)
        send_email.delay(
            'Code for email confirmation',
            'users/email/email_change_message.html',
            email,
            context
        )

    def __get_email_context(self, email):
        context = {
            'site_name': site.name,
            'code': self.__get_code(email),
        }
        return context

    def __get_code(self, email):
        try:
            code = EmailCode.objects.get(email=email)
        except ObjectDoesNotExist:
            pass
        else:
            code.delete()

        code = EmailCode.objects.create(email=email).code
        return code
