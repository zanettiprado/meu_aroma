from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import QuantityForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse
import logging


def all_products(request):
    products = Product.objects.all()
    query = None
    categories = None
    sort = None

    if request.GET:
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "Please enter a search term to find products.")
                return redirect(reverse('products'))

            queries = Q(name__icontains=query) | Q(description__icontains=query)
            products = products.filter(queries)

        # Sorting logic
        if 'sort' in request.GET:
            sort = request.GET['sort']
            if sort == 'price_asc':
                products = products.order_by('price')
            elif sort == 'price_desc':
                products = products.order_by('-price')
            elif sort == 'name_az':
                products = products.order_by('name')
            elif sort == 'name_za':
                products = products.order_by('-name')

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
    }

    return render(request, 'products/products.html', context)



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {})

    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            return redirect(request.POST.get('redirect_url', reverse('products')))  
        else:
            context = {'product': product, 'form': form}
            return render(request, 'product_detail.html', context)
    else:
        form = QuantityForm(initial={'quantity': 1})
    
    context = {
        'product': product,
        'form': form,
        'is_in_bag': str(product_id) in bag  # Check if the product is in the bag
    }
    return render(request, 'product_detail.html', context)  # Pass the entire context


def remove_from_bag(request, item_id):
    if request.method == 'POST':
        bag = request.session.get('bag', {})
        product_id = request.POST.get('product_id', None)
        origin = request.POST.get('origin', 'product_detail')  
        
        if product_id and product_id in bag:
            bag.pop(product_id)
            request.session['bag'] = bag
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Item removed'})
            
            
            if origin == 'bag':
                redirect_url = reverse('view_bag')  
            else:
                redirect_url = reverse('product_detail', kwargs={'product_id': product_id})

            return redirect(redirect_url)

        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Item not in bag'})
            messages.error(request, "The item wasn't in your bag.")
            
           
            if origin == 'bag':
                redirect_url = reverse('view_bag')  
            else:
                redirect_url = reverse('product_detail', kwargs={'product_id': product_id})

            return redirect(redirect_url)
    return HttpResponseBadRequest("Only POST requests are allowed on this endpoint.")