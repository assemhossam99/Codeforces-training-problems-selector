# Generated by Django 3.2.13 on 2023-03-10 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0003_problem_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastProblemUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lastUpdate', models.DateTimeField(null=True)),
            ],
        ),
    ]