from django.contrib import admin
from .models import User, Feedback, Report


admin.site.register(User)
admin.site.register(Feedback)
admin.site.register(Report)