from django.shortcuts import render, redirect
from django.contrib import messages 

from products.models import Product


def view_bag(request):
    return render(request, 'shopping_bag/bag.html')


def add_to_bag(request, product_id):
    
    if request.method == 'POST':
        product = Product.objects.get(pk=product_id)
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})

        if str(product_id) in bag:
            bag[str(product_id)] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[str(product_id)]}.')
        else:
            bag[str(product_id)] = quantity
            messages.success(request, f'Added {quantity} of {product.name} to your bag.')

        request.session['bag'] = bag
        return redirect(redirect_url)
    else:
        messages.error(request, f'Error adding product to your bag. Please try again.')
        return redirect('products')