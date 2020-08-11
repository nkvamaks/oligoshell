from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from . import forms


def user_login(request):
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request,
                username=cd['login'],
                password=cd['password'],
            )
            if user is None:
                return HttpResponse('BAD CREDS')
            else:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Auth success')
                else:
                    return HttpResponse('user inactive')
    else:
        form = forms.LoginForm()
    return render(request,
                  'authent/login.html',
                  {'form': form})
