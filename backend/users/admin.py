from django.contrib import admin

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("pk", "email", "username", "first_name", "last_name")
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("email", "username", "first_name", "last_name")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ("pk", "user", "author")
    search_fields = ("user", "author")
    list_filter = ("user", "author")
