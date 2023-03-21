from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from .models import User, Tag, Problem, LastProblemUpdate, Contest, Sheet
from django.db.models import Q
import requests
import random
import datetime


allProblems = []

def index(request):
    message = ""
    if request.method == "POST":
        ID = request.POST["id"]
        if 'delete-contest' in request.POST:
            Contest.objects.get(id=ID).delete()
        else:
            Sheet.objects.get(id=ID).delete()
        message = "Deleted"
    lastTime = LastProblemUpdate.objects.get(pk = 1).lastUpdate
    curTime = datetime.datetime.now()
    if  lastTime.day != curTime.day or lastTime.month != curTime.month or lastTime.year != curTime.year: 
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

    allContests = Contest.objects.all()
    userContests = []
    allContests = reversed(allContests)
    for contest in allContests:
        if len(userContests) == 5:
            break
        if request.user in contest.users.all():
            userContests.append(contest)

    allSheets = Sheet.objects.all()
    userSheets = []
    allSheets = reversed(allSheets)
    for sheet in allSheets:
        if len(userSheets) > 5:
            break
        if request.user in sheet.users.all():
            userSheets.append(sheet)
    return render(request, "problems/index.html", {
        'contests' : userContests,
        'sheets' : userSheets
    })

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "problems/login.html", {
                'message' : 'Invalid Username or Password'
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
            return render(request, "problems/register.html", {
                'message' : 'username is already taken'
            })
        login(request, user)
        updateUsersProblems(request)
        return render(request, 'problems/index.html')
    else:
        return render(request, "problems/register.html")

def updateUsersProblems(request):
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

def problems(request):
    if request.user.is_authenticated:
        updateUsersProblems(request)
        if "rating" in requests.get(f"https://codeforces.com/api/user.info?handles={request.user}").json()["result"][0]:
            userRating = int(requests.get(f"https://codeforces.com/api/user.info?handles={request.user}").json()["result"][0]["rating"])
        else:
            userRating = 800
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


def getProblems(problems, users):
    tmp = []
    for problem in problems:
        allUsers = True
        for user in users:
            if problem.users.filter(username = user).exists():
                allUsers = False
        if allUsers == True:
            tmp.append(problem)
    return random.choice(tmp)
            

def newContest(request):
    if request.method == "POST":
        import pytz
        errorMessage = ""
        users = request.POST["users"].replace(" ", "").split(',')
        for user in users:
            if not User.objects.filter(username=user).exists():
                errorMessage = f"user {user} is not registered"
        startDate = request.POST["startDate"]
        duration = request.POST["duration"]

        if duration == "" or int(duration) < 10:
            errorMessage = "Contest duration must be at least 10 minutes" 
        if errorMessage != "":
            return render(request, "problems/newContest.html", {
                'errorMessage' : errorMessage
            })
        contestProblems = []
        contestProblems.append(getProblems(Problem.objects.filter(rate__range=(800, 900)), users))
        contestProblems.append(getProblems(Problem.objects.filter(rate__range=(900, 1200)), users))
        contestProblems.append(getProblems(Problem.objects.filter(rate__range=(1200, 1600)), users))
        contestProblems.append(getProblems(Problem.objects.filter(rate__range=(1600, 2000)), users))
        contestProblems.append(getProblems(Problem.objects.filter(rate__range=(2000, 4000)), users))
        print(contestProblems)
        contest = Contest(duration=duration, startTime=startDate)
        contest.save()
        for user in users:
            contest.users.add(User.objects.get(username=user))
        for problem in contestProblems:
            contest.problems.add(problem)
        contest.save()
        return HttpResponseRedirect(f'contest/{contest.id}')
    return render(request, "problems/newContest.html")


def contest(request, contestID):
    import pytz
    contest = Contest.objects.get(id=contestID)
    contestProblems = contest.problems.all().order_by('rate')

    start = contest.startTime
    duration = contest.duration
    time_change = datetime.timedelta(minutes=duration)
    end = start + time_change
    end = end.replace(tzinfo=pytz.utc)
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.utc)
    ended = False
    if now > end:
        ended = True
    
    return render(request, "problems/contest.html", {
        'problems' : contestProblems,
        'id' : contestID,
        'end' : end,
        'ended' : ended
    })

def getProblem(problems, users, tags, problemNumbers):
    tmp = []
    for problem in problems:
        tagIn = False
        for tag in problem.tags.all():
            if tag.name in tags:
                tagIn = True
        allUsers = True
        for user in users:
            if problem.users.filter(username = user).exists():
                allUsers = False
        if allUsers == True and tagIn == True:
            tmp.append(problem)
    choosen = []
    while len(choosen) < problemNumbers:
        newProblem = random.choice(tmp)
        if newProblem not in choosen:
            choosen.append(newProblem)
    return choosen

def newSheet(request):
    if request.method == "POST":
        errorMessage = ""
        users = request.POST["users"].replace(" ", "").split(',')
        for user in users:
            if not User.objects.filter(username=user).exists():
                errorMessage = f"user {user} is not registered"
        tags=request.POST.getlist('tags')   
        minRate = request.POST['minRate']
        maxRate = request.POST['maxRate']
        if  minRate == "" or  int(minRate) < 800:
            minRate = 800
        if maxRate == "" or int(maxRate) > 4000:
            maxRate = 4000
        print(maxRate)
        problemNumbers = request.POST['problemsNumber']
        if int(problemNumbers) > 30:
            errorMessage = "Sheet can have 30 problems maximum"
        elif int(problemNumbers) <= 0:
            errorMessage = "Contest Should have at least one problem"
        if errorMessage != "":
            return render(request, "problems/newSheet.html", {
                'errorMessage' : errorMessage,
                'tags' : Tag.objects.all()
            })
        sheetProblems = []
        sheet = Sheet(maxRate=maxRate, minRate=minRate)
        sheet.save()
        if len(tags) == 0:
            for tag in Tag.objects.all():
                tags.append(tag.name)
        for tag in tags:
            sheet.tags.add(Tag.objects.get(name=tag))
        
        for user in users:
            sheet.users.add(User.objects.get(username=user))

        sheetProblems = getProblem(Problem.objects.filter(rate__range=(minRate, maxRate)), users, tags, int(problemNumbers))
        for problem in sheetProblems:
            sheet.problems.add(problem)
        sheet.save()
        return HttpResponseRedirect(f'sheet/{sheet.id}')
    return render(request, "problems/newSheet.html", {
        'tags' : Tag.objects.all()
    })

def sheet(request, sheetID):
    sheet = Sheet.objects.get(id=sheetID)
    sheetProblems = sheet.problems.all()

    return render(request, "problems/sheet.html", {
        'problems' : sheetProblems,
        'id' : sheetID
    })


def contests(request, username):
    allContests = Contest.objects.all()
    userContests = []
    for contest in allContests:
        if contest.users.filter(username=username).exists():
            userContests.append(contest)
    userContests = reversed(userContests)
    return render(request, "problems/contests.html", {
        'contests' : userContests
    })

def sheets(request, username):
    allSheets = Sheet.objects.all()
    userSheets = []
    for sheet in allSheets:
        if sheet.users.filter(username=username).exists():
            userSheets.append(sheet)
    userSheets = reversed(userSheets)
    return render(request, "problems/sheets.html", {
        'sheets' : userSheets
    })