# Generated by Django 4.1.1 on 2022-10-20 20:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_customusermodel_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customusermodel',
            options={'verbose_name': 'User'},
        ),
    ]