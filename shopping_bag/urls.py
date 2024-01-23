from django.urls import path
from . import views
from django.urls import path
from products.views import remove_from_bag 

urlpatterns = [
    path('', views.view_bag, name='view_bag'),
    path('add/<item_id>/', views.add_to_bag, name='add_to_bag'),
    path('add/<int:item_id>/', views.add_to_bag, name='add_to_bag'),
    path('remove/<item_id>/', remove_from_bag, name='shopping_bag_remove'),
    path('add_to_bag/<int:product_id>/', views.add_to_bag, name='add_to_bag'),
]