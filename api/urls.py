# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'well_matrix', views.WellMatrixViewSet, base_name='well_matrix')


urlpatterns = [
    path('authenticate/', views.AuthView.as_view()),
    path('', include(router.urls)),

    path('<int:pk>/', views.DetailUser.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]