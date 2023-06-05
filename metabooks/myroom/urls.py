from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('popup/',views.popup,name='popup'),
    path('popup/diary/',views.diary,name='diary'),
    path('popup/bookreport/',views.bookreport,name='bookreport'),
    path('popup/bookreport/display_img/', views.display_img, name='display_img'),
    path('popup/bookreport/db_list/',views.saving,name='db_list'),
    path('popup/bookreport/regen_img/',views.regen_img,name='regen_img'),
  ]
