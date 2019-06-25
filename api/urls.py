# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'feedback', views.FeedbackViewSet, base_name='feedback')
router.register(r'newsKZ', views.NewsKZViewSet, base_name='newsKZ')


urlpatterns = [
    path('authenticate/', views.AuthView.as_view()),
    path('', include(router.urls)),

    path('<int:pk>/', views.DetailUser.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]