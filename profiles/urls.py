from django.urls import path
from . import views
from .views import partner_application, partner_application_success

urlpatterns = [
    path('', views.profile, name='profile'),
    path('order_history/<order_number>', views.order_history, name='order_history'),
    path('partner-application/', partner_application, name='partner_application'),
    path('partner-application-success/', partner_application_success, name='partner_application_success'),
]
