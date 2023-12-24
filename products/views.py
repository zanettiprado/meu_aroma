from django.shortcuts import render, reverse, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category
from .forms import QuantityForm


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
    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            
            return redirect('some_cart_url')  
        else:
            context = {
                'product': product,
                'form': form
            }
            return render(request, 'product_detail.html', context)
    else:
        form = QuantityForm(initial={'quantity': 1})
    
    context = {
        'product': product,
        'form': form
    }
    return render(request, 'product_detail.html', context)