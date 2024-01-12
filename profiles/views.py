from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from checkout.models import Order
from .models import UserProfile
from .forms import UserProfileForm, PartnerApplicationForm


@login_required
def profile(request):
    """ Display the user's profile. """
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')

    form = UserProfileForm(instance=profile)
    orders = profile.orders.all()

    template = 'profiles/profile.html'
    context = {
        'form': form,
        'orders': orders,
        'on_profile_page': True
    }

    return render(request, template, context)


@login_required
def partner_application(request):
    if request.method == 'POST':
        form = PartnerApplicationForm(request.POST)
        if form.is_valid():
            partner_application = form.save(commit=False)
            partner_application.user = request.user
            partner_application.save()
            messages.success(request, 'Your application has been submitted successfully.')
            return redirect('partner_application_success')
    else:
        form = PartnerApplicationForm()

    return render(request, 'profiles/partner_application.html', {'form': form})

@login_required
def partner_application_success(request):
    return render(request, 'profiles/partner_application_success.html')


def order_history(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    messages.info(request, (
        f'This is your confirmation of your order {order_number}. '
        'A confirmation email was sent on the order date.'
    ))

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': True,
    }

    return render(request, template, context)


