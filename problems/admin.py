from django.contrib import admin
from .models import User, Tag, Problem, LastProblemUpdate

# Register your models here.

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Problem)
admin.site.register(LastProblemUpdate)