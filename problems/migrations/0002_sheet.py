# Generated by Django 3.2.13 on 2023-03-20 12:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('minRate', models.IntegerField(default=800)),
                ('maxRate', models.IntegerField(default=4000)),
                ('problems', models.ManyToManyField(related_name='sheets', to='problems.Problem')),
                ('tags', models.ManyToManyField(null=True, related_name='sheets', to='problems.Tag')),
                ('users', models.ManyToManyField(related_name='sheets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
