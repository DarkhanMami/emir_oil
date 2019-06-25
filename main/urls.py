from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('feedback', views.feedback, name='feedback'),

    path('generate_main_json', views.generate_main_json),
    path('generate_birge_data', views.generate_birge_data),
    path('generate_kz_news', views.generate_kz_news),
]