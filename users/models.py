import os
from PIL import Image
from datetime import timedelta
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
import random

profile_image_folder_name = 'ProfileImages'
default_profile_image_file_name = 'default.jpg'


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
		default=f'{profile_image_folder_name}/{default_profile_image_file_name}',
		validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])]
	)
	email = models.EmailField(unique=True, null=False, max_length=50)
	email_confirmed = models.BooleanField(default=False)
	last_name = None
	first_name = None

	class Meta:
		db_table = 'users'
		verbose_name = 'User'

	def get_absolute_url(self):
		return reverse('users:profile', kwargs={'username': self.username})

	def save(self, *args, **kwargs):
		super(CustomUserModel, self).save(*args, **kwargs)
		obj = CustomUserModel.objects.get(pk=self.pk)

		if self.profile_image.name != obj.profile_image.name:
			self.delete_profile_image_from_storage(obj)
	
			loaded_img = Image.open(self.profile_image.path)
			if loaded_img.height > 300 or loaded_img.width > 300:
				if loaded_img.mode != 'RGB':
					loaded_img = loaded_img.convert('RGB')
				loaded_img = loaded_img.resize((300, 300))
				loaded_img.save(self.profile_image.path)

	def delete(self, using=None, keep_parents=False):
		self.delete_profile_image_from_storage(CustomUserModel.objects.get(pk=self.pk))
		super(CustomUserModel, self).delete()

	@staticmethod
	def delete_profile_image_from_storage(user):
		if user.profile_image.name != f'{profile_image_folder_name}/{default_profile_image_file_name}':
			try:
				os.remove(user.profile_image.path)
			except FileNotFoundError:
				pass


class EmailCode(models.Model):
	email = models.EmailField(unique=True, null=False)
	code = models.IntegerField()
	expire_date = models.DateTimeField()

	class Meta:
		db_table = 'email_codes'

	def __str__(self):
		return str(self.code)

	def save(self, *args, **kwargs):
		self.code = random.randint(100000, 999999)
		self.expire_date = timezone.localtime() + timedelta(minutes=5)
		super(EmailCode, self).save(*args, **kwargs)
