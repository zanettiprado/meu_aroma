from django.urls import path, include
from . import views
from .webhooks import webhook
from .views import apply_coupon_view

urlpatterns = [
    path('', views.checkout, name='checkout'),
    path('checkout_success/<order_number>', views.checkout_success, name='checkout_success'),
    path('cache_checkout_data/', views.cache_checkout_data, name='cache_checkout_data'),
    path('wh/', webhook, name='webhook'),
    path('apply-coupon/', apply_coupon_view, name='apply_coupon'),
]