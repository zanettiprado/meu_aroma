from django.urls import path
from . import views
from .views import update_inventory

urlpatterns = [
    path('', views.all_products, name='products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('remove/<item_id>/', views.remove_from_bag, name='remove_from_bag'),
    path('add/', views.add_product, name='add_product'),
    path('edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/update_inventory/', update_inventory, name='update_inventory'),
    path('product/<int:product_id>/feedback/', views.product_feedback, name='product_feedback'),
]