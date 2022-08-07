from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from . import forms

# def user_login(request):
#     return render(request, 'oligoshell/profile.html', {'user': request.user})