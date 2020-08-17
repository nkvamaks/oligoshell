from django.urls import path

from . import views

app_name = 'oligoshell'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('seq<int:pk>/', views.SequenceDetailView.as_view(), name='sequence_detail'),
    path('order<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('seq_add/', views.SequenceCreateView.as_view(), name='sequence_create'),
    path('order_add/', views.OrderCreateView.as_view(), name='order_create'),
]
