from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Tag, Problem, LastProblemUpdate
from django.db.models import Q
import requests
import random
import datetime




# Create your views here.

allProblems = []

def index(request):

    lastTime = LastProblemUpdate.objects.get(pk = 1).lastUpdate
    curTime = datetime.datetime.now()
    if lastTime.day != curTime.day or lastTime.month != curTime.month or lastTime.year != curTime.year: 
        allProblems = requests.get(f"https://codeforces.com/api/problemset.problems").json()["result"]["problems"]
        
        for problem in allProblems:
            if len(Problem.objects.filter(contestID=problem["contestId"], index=problem["index"])) > 0:
                continue
            newProblem = Problem(name=problem["name"], index=problem["index"], contestID=problem["contestId"], rate =problem.get("rating"))
            newProblem.save()
            for tag in problem["tags"]:
                if len(Tag.objects.filter(name=tag)) == 0:
                    newTag = Tag.objects.create(name=tag)
                    newTag.save()
                    newProblem.tags.add(newTag)
                else:
                    newProblem.tags.add(Tag.objects.get(name=tag))
            newProblem.save()
        O = LastProblemUpdate.objects.get(pk = 1)
        O.lastUpdate = datetime.datetime.now()
        O.save()
    return render(request, "problems/index.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "problems/index.html", {
                'message' : 'can not log in'
            })
    return render(request, "problems/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        respond = requests.get(f"https://codeforces.com/api/user.info?handles={username}").json()
        if  respond['status'] == "FAILED":
            return render(request, "problems/register.html", {
                'message' : 'User is not registered on codeforces'
            })
        if password != confirmation:
            return render(request, "problems/register.html", {
                'message' : 'Password does not matchn'
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "problems/registe.html", {
                'message' : 'username is already taken'
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "problems/register.html")


def updatedToday(date):
    curDate = datetime.datetime.now()
    if date.year != curDate.year or date.month != curDate.month or date.year != curDate.year:
        return False
    return True

def problems(request):
    if request.user.is_authenticated:
        lastTime = request.user.lastUpdate
        curTime = datetime.datetime.now()
        if lastTime == None or lastTime.day != curTime.day or lastTime.month != curTime.month or lastTime.year != curTime.year:
            results = requests.get(f"https://codeforces.com/api/user.status?handle={request.user.username}").json()["result"]
            for result in results:
                verdict = result["verdict"]
                if len(result["problem"]["tags"]) > 0 and verdict == "OK" and result["contestId"] <= 1000000:
                    if len(Problem.objects.filter(contestID=result["contestId"], index=result["problem"]["index"])) == 0:
                        continue
                    accProblem = Problem.objects.get(contestID=result["contestId"], index=result["problem"]["index"])
                    if request.user in accProblem.users.all():
                        continue
                    accProblem.users.add(request.user)
                    accProblem.save()
                    
            request.user.lastUpdate = datetime.datetime.now()
            request.user.save()
        userRating = int(requests.get(f"https://codeforces.com/api/user.info?handles={request.user}").json()["result"][0]["rating"])
        userRating = (userRating // 100) * 100
        minRating = max(800, userRating - 200)
        maxRating = min(4000, userRating + 400)
        userProblems = []
        print(request.user)
        for curRate in range(minRating, maxRating, 100):
            print(curRate)
            tmpList = []
            for problem in Problem.objects.exclude(~Q(rate=curRate) | Q(rate=None)):
                if not problem.users.filter(username=request.user.username).exists():
                    tmpList.append(problem)
            print(len(tmpList))
            userProblems.append(random.choice(tmpList))

        return render(request, "problems/problems.html", {
            'problems' : userProblems
        })
    return render(request, "problems/login.html")
            
    