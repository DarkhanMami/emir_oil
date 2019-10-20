# api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'well_matrix', views.WellMatrixViewSet, base_name='well_matrix')
router.register(r'field_balance', views.FieldBalanceViewSet, base_name='field_balance')
router.register(r'fields', views.FieldViewSet, base_name='fields')
router.register(r'wells', views.WellViewSet, base_name='wells')
router.register(r'production', views.ProductionViewSet, base_name='production')
router.register(r'park_production', views.ParkProductionViewSet, base_name='park_production')
router.register(r'park_oil', views.ParkOilViewSet, base_name='park_oil')
router.register(r'report_excel', views.ReportExcelViewSet, base_name='report_excel')

urlpatterns = [
    path('authenticate/', views.AuthView.as_view()),
    path('', include(router.urls)),
    path('add_today_data/', views.add_today_data),
    path('<int:pk>/', views.DetailUser.as_view()),
    path('rest-auth/', include('rest_auth.urls')),
]