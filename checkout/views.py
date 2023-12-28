from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from products.models import Product

def checkout(request):
    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, "Your bag is empty!")
        return redirect(reverse('products'))

    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        if order_form.is_valid():
            return redirect('success_url')
        else:
            messages.error(request, "There was an error with your form. Please check your information.")
    else:
        order_form = OrderForm()

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

    context = {
        'order_form': order_form,
        'bag_items': bag_items,
        'total': total,
    }

    return render(request, 'checkout/checkout.html', context)
