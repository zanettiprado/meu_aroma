from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from shopping_bag.context import bag_contents

import stripe 

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    order_form = OrderForm(request.POST or None)
    if request.method == 'POST' and order_form.is_valid():
        bag = request.session.get('bag', {})
        order = order_form.save()
        for item_id, quantity in bag.items():
            try:
                product = Product.objects.get(id=item_id)
                OrderLineItem.objects.create(order=order, product=product, quantity=quantity)
            except Product.DoesNotExist:
                messages.error(request, (
                    "One of the items in your shopping bag was not found in our database. "
                    "Please contact customer support for assistance.")
                )
                order.delete()
                return redirect(reverse('shopping_bag'))

        request.session['save_info'] = 'save-info' in request.POST
        print("Redirecting to checkout success")
        return redirect(reverse('checkout_success', args=[order.order_number]))

    else:
        bag = request.session.get('bag', {})
        if not bag:
            messages.error(request, "Your shopping bag is currently empty, add some products before checking out.")
            print("Rendering checkout page with form")
            return redirect(reverse('products'))

        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100)
        try:
            intent = stripe.PaymentIntent.create(amount=stripe_total, currency=settings.STRIPE_CURRENCY)
        except stripe.error.StripeError as e:
            messages.error(request, "Failed to create a payment intent: " + str(e))
            return redirect(reverse('checkout'))
        
        if not stripe_public_key:
            messages.warning(request, 'It appears the Stripe public key is missing. Please confirm it has been set.')

        bag_items = [{
            'product_id': pid,
            'quantity': qty,
            'product': Product.objects.get(id=pid),
            'subtotal': qty * Product.objects.get(id=pid).price
        } for pid, qty in bag.items()]

        context = {
            'order_form': order_form,
            'bag_items': bag_items,
            'total': total,
            'stripe_public_key': stripe_public_key,
            'client_secret': intent.client_secret if 'intent' in locals() else None,
        }
        
    return render(request, 'checkout/checkout.html', context)

def checkout_success(request, order_number):
 
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)
    messages.success(request, f'Congratulations, your order has been successfully processed! \
        Your order reference is {order_number}. A confirmation \
        email is on its way to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }
    print(f"Order {order_number} processed successfully")
    return render(request, template, context)