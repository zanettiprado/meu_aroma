from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Inventory
from checkout.models import Order, OrderLineItem
from profiles.models import UserProfile
from .forms import QuantityForm, ProductForm, InventoryForm, FeedbackForm, Feedback
from django.http import JsonResponse, HttpResponseBadRequest
from django.urls import reverse


import logging


def all_products(request):
    """
    View function for displaying all products, with optional filtering and sorting.
    """

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
            if products.count() == 0:
                messages.error(request,
                               "No products found matching your criteria.")

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

    return render(request,
                  'products/products.html', context)


def product_detail(request, product_id):
    """
    View function for displaying the details of a specific product, including its
    description, inventory, feedback, and options to add it to the shopping bag.
    """

    product = get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {})
    inventory = Inventory.objects.filter(product=product).first()
    if not inventory:
        inventory = Inventory(product=product,
                              quantity_in_stock=0, quantity_allocated=0)

    has_purchased = False
    if request.user.is_authenticated:
        has_purchased = user_has_purchased(request.user, product)

    feedback_form = FeedbackForm()
    feedbacks = Feedback.objects.filter(product=product)

    if request.method == 'POST':
        form = QuantityForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            bag[product_id] = bag.get(product_id, 0) + quantity
            request.session['bag'] = bag
            messages.success(request, f"{quantity} of {product.name} added to your bag.")
            return redirect(request.POST.get('redirect_url',
                                             reverse('products')))
        else:
            messages.error(request, "There was an error with your form. Please check your input.")
            context = {'product': product, 'form': form}
            return render(request, 'product_detail.html',
                          context)
    else:
        form = QuantityForm(initial={'quantity': 1})

    context = {
        'product': product,
        'inventory': inventory,
        'form': form,
        'is_in_bag': str(product_id) in bag,
        'feedback_form': feedback_form,
        'user_has_purchased': has_purchased,
        'feedbacks': feedbacks,
    }

    return render(request, 'products/product_detail.html',
                  context)


def remove_from_bag(request, item_id):
    """
    View function for removing a product from the shopping bag.
    """

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        product_id = request.POST.get('product_id', None)
        origin = request.POST.get('origin', 'product_detail')

        if product_id and product_id in bag:
            bag.pop(product_id)
            request.session['bag'] = bag

            messages.success(request, "Product removed from your bag successfully.")

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
                redirect_url = reverse('product_detail',
                                       kwargs={'product_id': product_id})

            return redirect(redirect_url)

    return HttpResponseBadRequest("Invalid request. Only POST requests are allowed on this endpoint.")


@login_required
def add_product(request):
    """
    View function for adding a new product to the store.
    """

    if not request.user.is_superuser:
        messages.error(request,
                       'Sorry, you are not allowed to access this page.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Added product: {product.name}')
            return redirect('product_detail', product_id=product.id)
        else:
            messages.error(request,
                           'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    template = 'products/add_product.html'
    context = {
        'form': form,
        'is_adding_product': True,
    }

    return render(request, template, context)


@login_required
def edit_product(request, product_id):
    """
    View function for editing an existing product in the store.
    """

    if not request.user.is_superuser:
        messages.error(request,
                       'Sorry, you are not allowed to access this page.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST,
                           request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request,
                             'Successfully updated product!')
            return redirect(reverse('product_detail',
                                    args=[product.id]))
        else:
            messages.error(request,
                           'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request,
                      f'You are editing {product.name}')

    template = 'products/edit_product.html'
    context = {
        'form': form,
        'is_editing_product': True,
        'product': product,

    }

    return render(request,
                  template, context)


@login_required
def delete_product(request, product_id):
    """
    View function for deleting an existing product from the store.
    """

    if not request.user.is_superuser:
        messages.error(request,
                       'Sorry, you are not allowed to access this page.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product,
                                pk=product_id)

    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product successfully deleted!')
        return redirect(reverse('products'))

    template = 'products/delete_product.html'
    context = {
        'product': product,
    }

    return render(request, template, context)


@login_required
def update_inventory(request,
                     product_id):
    """
    View function for updating the inventory of a product in the store.
    """

    if not request.user.is_superuser:
        messages.error(request, 'Only store managers can update inventory.')
        return redirect('product_detail',
                        product_id=product_id)

    product = get_object_or_404(Product,
                                pk=product_id)
    inventory, created = Inventory.objects.get_or_create(product=product)

    if request.method == 'POST':
        form = InventoryForm(request.POST, instance=inventory)
        if form.is_valid():
            form.save()
            messages.success(request, 'Inventory updated successfully.')
            return redirect('product_detail',
                            product_id=product_id)
        else:
            messages.error(request,
                           'Failed to update inventory. Please check the form.')
    else:
        form = InventoryForm(instance=inventory)

    context = {
        'form': form,
        'product': product
    }

    return render(request, 'products/update_inventory.html', context)


@login_required
def product_feedback(request, product_id):
    """
    View function for allowing users to submit feedback for a product.
    """
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.product = product
            feedback.user = request.user
            feedback.save()
            messages.success(request,
                             'Your feedback has been submitted.')
            return redirect('product_detail',
                            product_id=product.id)
        else:
            messages.error(request,
                           'There was an error with your feedback submission. Please check your input.')
    else:
        form = FeedbackForm()

    context = {
        'form': form,
        'product': product
    }

    return render(request,
                  'products/product_feedback.html', context)


def user_has_purchased(user, product):
    """
    Check if the given user has purchased the given product.
    """
    # Using the user's profile to filter orders
    user_profile = UserProfile.objects.get(user=user)
    return OrderLineItem.objects.filter(order__user_profile=user_profile, product=product).exists()
