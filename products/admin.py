from django.contrib import admin
from .models import Category, Product, Inventory, Feedback

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_in_stock', 'quantity_allocated')

admin.site.register(Inventory, InventoryAdmin)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'comment', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('comment',)