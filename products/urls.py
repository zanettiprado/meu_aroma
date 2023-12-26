from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('remove/<item_id>/', views.remove_from_bag, name='remove_from_bag'),
]
