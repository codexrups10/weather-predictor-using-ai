"""
URL configuration for weather_predictor app
"""

from django.urls import path
from . import views

app_name = 'weather_predictor'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),

    # API endpoints
    path('api/predict/', views.predict_weather, name='predict_weather'),
    path('api/model-info/', views.model_info, name='model_info'),
    path('api/health/', views.health_check, name='health_check'),
]
