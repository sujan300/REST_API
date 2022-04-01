"""project URL Configuration
"""
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/user/",include("api_account.urls")),
]
