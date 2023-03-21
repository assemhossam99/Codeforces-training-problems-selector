from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_view"),
    path('logout', views.logout_view, name = "logout_view"),
    path('register', views.register_view, name="register_view"),
    path('problems', views.problems, name="problems"),
    path('newContest', views.newContest, name="newContest"),
    path('newSheet', views.newSheet, name="newSheet"),
    path('contest/<int:contestID>', views.contest, name="contest"),
    path('sheet/<int:sheetID>', views.sheet, name="sheet"),
    path('contests/<str:username>', views.contests, name="contests"),
    path('sheets/<str:username>', views.sheets, name="sheets")
]