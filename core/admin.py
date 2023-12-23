from django.contrib import admin
from .models import User, Feedback, Report


class FeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "title",
        "text",
        "user",
        "created_on",
    )
    list_filter = (
        "user",
        
    )


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "account_type",
        "email",
        "phone",
        "brand_name",
        "firstname",
        "lastname",
        "sex",
        "email_verified",
        "phone_verified",
        "is_active",
        "created_at"
    )
    list_filter = (
        "account_type",
        "sex",
        "email_verified",
        "phone_verified",
        "is_active",
        
    )

class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "recipient",
        "title",
        "text",
        "user",
        "created_on",
    )
    list_filter = (
        "user",
        "recipient",
        
    )
admin.site.register(User, UserAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Report, ReportAdmin)