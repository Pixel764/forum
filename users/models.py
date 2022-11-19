import os

from datetime import timedelta
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import random

profile_image_folder_name = 'ProfileImages'
profile_image_file_name = 'default.jpg'


class CustomUserModel(AbstractUser):
	username_validator = UnicodeUsernameValidator

	username = models.CharField(
		'username',
		max_length=30,
		unique=True,
		help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
		validators=[username_validator],
		error_messages={
			'unique': 'A user with that username already exists.',
		},
	)
	profile_image = models.ImageField(
		upload_to=profile_image_folder_name,
		default=f'{profile_image_folder_name}/{profile_image_file_name}',
		validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg', 'gif', 'bmp'])]
	)
	email = models.EmailField(unique=True, null=False, max_length=50)
	email_confirmed = models.BooleanField(default=False)
	last_name = None
	first_name = None

	class Meta:
		db_table = 'users_user_model'
		verbose_name = 'User'

	def get_absolute_url(self):
		return reverse('users:profile', kwargs={'username': self.username})

	def save(self, *args, **kwargs):
		obj = CustomUserModel.objects.filter(pk=self.pk)
		if obj:
			self.delete_profile_image_from_storage(obj[0])
		return super(CustomUserModel, self).save(*args, **kwargs)

	def delete(self, using=None, keep_parents=False):
		self.delete_profile_image_from_storage(CustomUserModel.objects.get(pk=self.pk), user_delete=True)
		return super(CustomUserModel, self).delete()

	def delete_profile_image_from_storage(self, user, **kwargs):
		def delete_image():
			try:
				os.remove(user.profile_image.path)
			except FileNotFoundError:
				pass

		if kwargs.get('user_delete', False) or user.profile_image.name != self.profile_image.name:
			if user.profile_image.name != f'{profile_image_folder_name}/{profile_image_file_name}':
				delete_image()


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
