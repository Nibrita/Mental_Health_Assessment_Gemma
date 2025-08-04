from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render, redirect


def root_redirect_or_home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/home.html')

urlpatterns = [
    path('', root_redirect_or_home, name='home'),
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
]
