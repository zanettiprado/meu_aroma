from django.shortcuts import render, redirect


def view_bag(request):
    return render(request, 'shopping_bag/bag.html')


def add_to_bag(request, product_id):
    if request.method == 'POST':
        
        quantity = int(request.POST.get('quantity', 1))
        redirect_url = request.POST.get('redirect_url')
        bag = request.session.get('bag', {})

        if str(product_id) in bag:
            bag[str(product_id)] += quantity
        else:
            bag[str(product_id)] = quantity

        request.session['bag'] = bag
        return redirect(redirect_url)
    else:
        
        return redirect('products')