# Generated by Django 3.2.13 on 2023-03-18 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='rate',
            field=models.IntegerField(null=True),
        ),
    ]