from django.urls import path
from . import views

app_name = 'statistiques'

urlpatterns = [
    path('', views.vue_statistiques, name='index'),
    path('export/csv/', views.vue_export_csv, name='export_csv'),
]