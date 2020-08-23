from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'oligoshell'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('seq<int:pk>/', views.SequenceDetailView.as_view(), name='sequence_detail'),
    path('order<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('seq_add/', views.SequenceCreateView.as_view(), name='sequence_create'),
    path('order_add/', views.OrderCreateView.as_view(), name='order_create'),
    path('profile/', views.view_profile, name='profile'),
    path('batch/', views.all_batches, name='batch'),
    path('batch/<int:pk>/', views.batch_details, name='batch_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)