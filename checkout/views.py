from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from django.conf import settings
from products.models import Product
from shopping_bag.context import bag_contents

import stripe 


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "Your bag is empty!")
        return redirect(reverse('products'))
    
    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    total_in_cents = round(total * 100) 

    stripe.api_key = stripe_secret_key  
    try:
        
        intent = stripe.PaymentIntent.create(
            amount=total_in_cents,
            currency=settings.STRIPE_CURRENCY,
        )
    except stripe.error.StripeError as e:
        messages.error(request, "An error occurred while creating a payment intent: " + str(e))
        return redirect(reverse('checkout'))
    
    print(intent)
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            return redirect('success_url')
        else:
            messages.error(request, "There was an error with your form. Please check your information.")
    else:
        order_form = OrderForm()


    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
            Did you forget to set it in your environment?')
        
    # Retrieve the bag items and their details
    bag_items = []
    total = 0
    product_count = 0
    for product_id, quantity in bag.items():
        product = Product.objects.get(id=product_id)
        total += quantity * product.price
        product_count += quantity
        bag_items.append({
            'product_id': product_id,
            'quantity': quantity,
            'product': product,
            'subtotal': quantity * product.price
        })

    # Preparing the context
    context = {
        'order_form': order_form,
        'bag_items': bag_items,
        'total': total,
        'stripe_public_key': 'stripe_public_key',
        'client_secret': intent.client_secret,    
    }

    return render(request, 'checkout/checkout.html', context)
