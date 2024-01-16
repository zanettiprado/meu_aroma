from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.html import strip_tags

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
    """
    Handle partner application form submission.

    This view handles the submission of the partner application form. If the form is valid,
    it creates a new partner application record and sends an email notification.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered partner application form or a success page on successful submission.

    """
    if request.method == 'POST':
        form = PartnerApplicationForm(request.POST)
        if form.is_valid():
            partner_application = form.save(commit=False)
            partner_application.user = request.user
            partner_application.save()
            
            # Send an email notification          
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            company_name = form.cleaned_data.get('company_name')
            phone_number = form.cleaned_data.get('phone_number')
            additional_info = form.cleaned_data.get('additional_info')

            subject = 'New Partnership Application'
            
            message = f'New partnership application received from {name}.\n\n'
            message += f'Email: {email}\n'
            message += f'Company Name: {company_name}\n'
            message += f'Phone Number: {phone_number}\n'
            message += f'Additional Information: {additional_info}'

            recipient_email = 'zanettipradospam@gmail.com' 
            
            sender_email = email
            send_mail(subject, strip_tags(message), sender_email, [recipient_email], html_message=message)
                       
            messages.success(request, 'Your application has been submitted successfully.')
            return redirect('partner_application_success')
    else:
        form = PartnerApplicationForm()

    return render(request, 'profiles/partner_application.html', {'form': form})

@login_required
def partner_application_success(request):
    """
    Display a success message after submitting a partner application.

    This view displays a success message to the user after successfully submitting a partner application.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered partner application success template.

    """
    return render(request, 'profiles/partner_application_success.html')


def order_history(request, order_number):
    """
    Display order history details for a specific order.

    This view displays the order details for a specific order in the user's order history.

    Args:
        request (HttpRequest): The HTTP request object.
        order_number (str): The order number to retrieve order details for.

    Returns:
        HttpResponse: The rendered order details template for the specified order.

    """
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


