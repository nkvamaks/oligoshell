from django.urls import path

from . import views

app_name = 'oligoshell'
urlpatterns = [
    path('', views.index, name='index'),
]
