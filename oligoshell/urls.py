from django.urls import path

from . import views

app_name = 'oligoshell'
urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('seq<int:pk>/', views.SequenceDetailView.as_view(), name='sequence_detail'),
    path('order<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    # path('order<int:order_id>/seq<int:seq_id>/', views.sequence_detail, name='sequence_detail'),
    # path('order<int:order_id>/', views.order_detail, name='order_detail'),
]
