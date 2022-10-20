from django.template.loader import render_to_string
from project.celery import app
from django.conf import settings
from django.core.mail import send_mail
from .models import EmailCode
from django.utils import timezone


@app.task(ignore_result=True)
def send_email(subject, message_template, user_email, context):
    send_mail(
        subject=subject,
        html_message=render_to_string(message_template, context=context),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email],
        message=None,
    )


@app.task()
def delete_expired_email_codes():
    EmailCode.objects.filter(expire_date__lte=timezone.now()).delete()
