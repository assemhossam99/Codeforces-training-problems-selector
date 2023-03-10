from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User
import requests

# Create your views here.

allProblems = requests.get(f"https://codeforces.com/api/problemset.problems").json()["result"]

def index(request):
    return render(request, "problems/layout.html")

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


def problems(request):
    if request.user.is_authenticated:
        user = request.user
        respond = requests.get(f"https://codeforces.com/api/user.status?handle={user.username}").json()["result"]
        solvedProblems = []
        for problem in respond:
            solvedProblems.append(problem["problem"])
        
        # for problem in allProblems:
        #     if problem not in solvedProblems:
        #         unsolvedProblems.append(problem)
        return render(request, "problems/problems.html", {
            'solvedProblems' : solvedProblems,
            'allProblems' : allProblems["problems"]
        })
    else:
        return HttpResponseRedirect("index")
        