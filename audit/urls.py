from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.vue_audit, name='index'),
    path('analyser/<str:id_tx>/', views.vue_analyser_transaction, name='analyser'),
]