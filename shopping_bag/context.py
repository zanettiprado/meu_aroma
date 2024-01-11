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
        item_subtotal = quantity * product.price  # Calculate the subtotal for each item
        total += item_subtotal
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'quantity': quantity,
            'product': product,
            'subtotal': item_subtotal,  # Add the subtotal for each item
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
    # Calculate discount (if coupon is valid)
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
    
    subtotal_after_discount = total - discount_amount
    
    if subtotal_after_discount < settings.FREE_DELIVERY_THRESHOLD:
        delivery = subtotal_after_discount * Decimal(settings.STANDARD_DELIVERY_PERCENTAGE / 100)
        free_delivery_delta = settings.FREE_DELIVERY_THRESHOLD - subtotal_after_discount
    else:
        delivery = 0
        free_delivery_delta = 0
    
    # Apply the coupon discount to the grand total check if is correct
    grand_total = subtotal_after_discount + delivery
    print(f'grand_total: {grand_total}')

    context = {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'subtotal_after_discount': subtotal_after_discount,
        'discount_amount': discount_amount,
        'grand_total': grand_total,
        'last_added_product': last_added_product,
        'last_added_quantity': last_added_quantity,
    }

    return context