from django.contrib import admin
from .models import User, Tag, Problem, LastProblemUpdate, Contest

# Register your models here.

admin.site.register(User)
admin.site.register(Tag)
admin.site.register(Problem)
admin.site.register(LastProblemUpdate)
admin.site.register(Contest)