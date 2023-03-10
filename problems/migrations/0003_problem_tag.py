# Generated by Django 3.2.13 on 2023-03-10 22:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0002_user_lastupdate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('index', models.CharField(max_length=4)),
                ('contestID', models.IntegerField()),
                ('tags', models.ManyToManyField(related_name='problems', to='problems.Tag')),
                ('users', models.ManyToManyField(related_name='problems', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
