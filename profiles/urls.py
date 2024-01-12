from django.urls import path
from . import views
from .views import partner_application

urlpatterns = [
    path('', views.profile, name='profile'),
    path('order_history/<order_number>', views.order_history, name='order_history'),
    path('partner-application/', partner_application, name='partner_application'),
]
