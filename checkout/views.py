from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
from django.contrib import messages
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.models import UserProfile
from profiles.forms import UserProfileForm
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
        
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(initial={
                    'full_name': profile.user.get_full_name(),
                    'email': profile.user.email,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'phone_number': profile.default_phone_number,
                    'town_or_city': profile.default_town_or_city,
                    'county': profile.default_county,
                    'postcode': profile.default_postcode,
                })
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()
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
    
    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
      
        order.user_profile = profile
        order.save()

        if save_info:
            profile_data = {
                'default_street_address1': order.street_address1,
                'default_street_address2': order.street_address2,
                'default_phone_number': order.phone_number,
                'default_town_or_city': order.town_or_city,
                'default_county': order.county,
                'default_postcode': order.postcode,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)