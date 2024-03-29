from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    lastUpdate = models.DateTimeField(null=True)
    rating = models.IntegerField(default=0)

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
    rate = models.IntegerField(null=True)
    tags = models.ManyToManyField(Tag, related_name="problems")
    users = models.ManyToManyField(User, related_name="problems")

    def __str__(self):
        return f"{self.index}-{self.name}"

class Contest(models.Model):
    startTime = models.DateTimeField(null=True)
    duration = models.IntegerField()
    problems = models.ManyToManyField(Problem, related_name="contests")
    users = models.ManyToManyField(User,related_name="contests")

    def __str__(self):
        return f"Contest - {self.id}"

class Sheet(models.Model):
    minRate = models.IntegerField(default=800)
    maxRate = models.IntegerField(default=4000)
    problems = models.ManyToManyField(Problem, related_name="sheets")
    users = models.ManyToManyField(User, related_name="sheets")
    tags = models.ManyToManyField(Tag, related_name="sheets", null=True)

    def __str__(self):
        return f"Sheet - {self.id}"

class Standing(models.Model):
    score1 = models.IntegerField(default=-1)
    score2 = models.IntegerField(default=-1)
    score3 = models.IntegerField(default=-1)
    score4 = models.IntegerField(default=-1)
    score5 = models.IntegerField(default=-1)
    totalScore = models.IntegerField(default=0)
    problemCnt = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)

    def __str__(self):
        return f"User - {self.user.id} in Contest {self.contest.id}"