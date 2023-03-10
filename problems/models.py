from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    lastUpdate = models.DateTimeField(null=True)

class LastProblemUpdate(models.Model):
    lastUpdate = models.DateTimeField(null=True)

class Tag(models.Model):
    name = models.CharField(max_length = 128)

    def __str__(self):
        return f"{self.id}: {self.name}"

class Problem(models.Model):
    name = models.CharField(max_length = 128)
    index = models.CharField(max_length = 4)
    contestID = models.IntegerField()
    tags = models.ManyToManyField(Tag, related_name="problems")
    users = models.ManyToManyField(User, related_name="problems")

    def __str__(self):
        return f"{self.index}-{self.name}"

