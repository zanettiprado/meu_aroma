from django.contrib import admin
from .models import Order, OrderLineItem, Coupon

class OrderLineItemAdminInline(admin.TabularInline):
    """
    Inline admin class for OrderLineItem model to be displayed within the Order admin page.
    """
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)

class OrderAdmin(admin.ModelAdmin):
    """
    Admin class for the Order model, allowing customization of the admin interface.
    """
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date',
                       'delivery_cost',
                       'order_total',
                       'grand_total',
                       'coupon')

    fields = (
        'order_number',
        'user_profile', 'date',
        'full_name', 'email', 'phone_number',
        'country', 'postcode', 'town_or_city',
        'street_address1',
        'street_address2', 'county', 'delivery_cost',
        'order_total', 'grand_total', 'coupon'
    )

    list_display = ('order_number', 'date',
                    'full_name', 'order_total',
                    'delivery_cost', 'grand_total',
                    'coupon')

    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """
    Admin class for the Coupon model, allowing customization of the admin interface.
    """
    list_display = ['code', 'valid_from',
                    'valid_to', 'discount',
                    'active']
    list_filter = ['active', 'valid_from',
                   'valid_to']
    search_fields = ['code']
