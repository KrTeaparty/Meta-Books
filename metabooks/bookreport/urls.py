from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('display_img/', views.display_img, name='display_img'),
    path('db_list/', views.saving, name='db_list'),
    path('regen_img/', views.regen_img, name='regen_img')
]
