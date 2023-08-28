from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('gera-senha/', views.gera_senha, name='gera-senha'),
]