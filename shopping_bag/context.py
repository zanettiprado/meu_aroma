from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from products.models import Product
from checkout.models import Coupon  


def bag_contents(request):

    bag_items = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    last_added_product_id = request.session.get('last_added_product_id', None)
    last_added_product = None
    last_added_quantity = 0

    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        total += quantity * product.price
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
        })

        # Check and set the details for the last added product
        if str(item_id) == str(last_added_product_id):
            last_added_product = product
            last_added_quantity = quantity

    if total < settings.FREE_DELIVERY_THRESHOLD:
        delivery = total * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - total
    else:
        delivery = 0
        free_delivery_delta = 0

    # Updated the context with the cupon check if is necessary 
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0  # Initialize the discount amount to 0

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            if coupon.is_valid():
                # Calculate the discount amount based on the coupon's discount percentage
                discount_amount = (total * coupon.discount) / 100
        except Coupon.DoesNotExist:
            pass  

    # Apply the coupon discount to the grand total check if is correct
    grand_total = (delivery + total) - discount_amount

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
        'last_added_product': last_added_product,
        'last_added_quantity': last_added_quantity, 
    }

    return context