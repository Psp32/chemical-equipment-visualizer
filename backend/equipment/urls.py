from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_csv, name='upload_csv'),
    path('summary/', views.get_summary, name='get_summary'),
    path('summary/<int:dataset_id>/', views.get_summary, name='get_summary_by_id'),
    path('data/', views.get_data, name='get_data'),
    path('data/<int:dataset_id>/', views.get_data, name='get_data_by_id'),
    path('history/', views.get_history, name='get_history'),
    path('pdf/', views.generate_pdf, name='generate_pdf'),
    path('pdf/<int:dataset_id>/', views.generate_pdf, name='generate_pdf_by_id'),
]
