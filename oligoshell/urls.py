from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'oligoshell'

urlpatterns = [
    path('', views.IndexListView.as_view(), name='index'),
    path('order_add/', views.OrderCreateView.as_view(), name='order_create'),

    path('seq<int:pk>/', views.SequenceUpdateView.as_view(), name='sequence_detail'),
    path('order<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('seq_add/', views.SequenceCreateView.as_view(), name='sequence_create'),
    # path('seq_formset_add/', views.SequenceFormSetView.as_view(), name='sequence_formset'),
    # path('order_and_seqs_add/', views.OrderInlineCreateView.as_view(), name='order_and_seqs'),
    path('batch_add/', views.BatchCreateView.as_view(), name='batch_create'),
    path('purification_add/', views.PurificationCreateView.as_view(), name='purification_create'),
    path('batch/<int:pk>/', views.purification_details, name='purification_details'),
    path('profile/', views.view_profile, name='profile'),
    path('register/', views.register, name='register'),
    path('batch/', views.all_batches, name='batch'),
    path('batch/<int:pk>/', views.batch_details, name='batch_details'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)