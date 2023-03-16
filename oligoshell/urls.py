from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'oligoshell'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('order_add/', views.OrderCreateView.as_view(), name='order_create'),
    path('seq<int:pk>/', views.SequenceUpdateView.as_view(), name='sequence_detail'),
    path('order<int:pk>/', views.OrderUpdateView.as_view(), name='order_detail'),
    path('seq_add/', views.SequenceCreateView.as_view(), name='sequence_create'),
    path('batch_add/', views.BatchCreateView.as_view(), name='batch_create'),
    path('purification_add/', views.PurificationCreateView.as_view(), name='purification_create'),
    path('purification/<int:pk>/', views.PurificationUpdateView.as_view(), name='purification_details'),
    path('profile/', views.view_profile, name='profile'),
    path('register/', views.register, name='register'),
    path('batch/<int:pk>/', views.BatchUpdateView.as_view(), name='batch_details'),
    path('search/', views.SearchResultsListView.as_view(), name='search_results'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)