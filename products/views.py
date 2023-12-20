from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product

# Create your views here.

def all_products(request):
    products = Product.objects.all()
    query = None 

    if request.GET.get('q'):
        query = request.GET['q']
        if not query:
            messages.error(request, "Please enter a search term to find products.")
            return redirect(reverse('products'))

        queries = Q(name__icontains=query) | Q(description__icontains=query) # returning search result for description or name
        products = products.filter(queries)

    context = {
        'products': products,
        'search_term': query,
    }

    return render(request, 'products/products.html', context)



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {
        'product': product
    }
    return render(request, 'product_detail.html', context)