from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('generate_production', views.generate_production),
    path('generate_park_production', views.generate_park_production),
]