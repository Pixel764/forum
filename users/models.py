from datetime import timedelta
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import random

profile_image_directory = 'ProfileImages'


class CustomUserModel(AbstractUser):
    profile_image = models.ImageField(upload_to=profile_image_directory,
                                      default='ProfileImages/default.jpg',
                                      validators=[FileExtensionValidator(
                                          allowed_extensions=['png', 'jpeg', 'jpg', 'gif', 'bmp'])])
    email = models.EmailField(unique=True, null=False)
    email_confirmed = models.BooleanField(default=False)
    last_name = None
    first_name = None

    class Meta:
        db_table = 'users_user_model'

    def get_absolute_url(self):
        return reverse('users:profile', kwargs={'username': self.username})


class EmailCode(models.Model):
    email = models.EmailField(unique=True, null=False)
    code = models.IntegerField()
    expire_date = models.DateTimeField()

    class Meta:
        db_table = 'users_email_code'

    def __str__(self):
        return str(self.code)

    def save(self, *args, **kwargs):
        self.code = random.randint(100000, 999999)
        self.expire_date = timezone.localtime() + timedelta(minutes=5)
        super(EmailCode, self).save(*args, **kwargs)
