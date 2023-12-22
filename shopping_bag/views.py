from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product 
# Create your views here.

def view_bag(request):
    
    return render(request, 'shopping_bag/bag.html')


def add_to_bag(request, item_id):
       
    # product = get_object_or_404(Product, pk=item_id)  
    quantity = int(request.POST.get('quantity'))  
    redirect_url = request.POST.get('redirect_url')

    bag = request.session.get('bag', {})  
    
    if item_id in bag:
        bag[item_id] += quantity  
    else:
        bag[item_id] = quantity  

    request.session['bag'] = bag
    
    print(request.session['bag'])  
    # messages.success(request, f'Added {product.name} to your bag, keep buying')

    return redirect(redirect_url)