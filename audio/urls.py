from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('home/', views.index, name='home'),
	path('home/', views.imageProcessor, name='home'),
	path('result/', views.search, name='result'),

]