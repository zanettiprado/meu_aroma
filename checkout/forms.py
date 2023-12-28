from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'postcode', 'town_or_city', 'street_address1',
            'street_address2', 'country', 'county'
        )

    def __init__(self, *args, **kwargs):

        super(OrderForm, self).__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'country': 'Country',
            'county': 'County, State or Locality',
        }

        # Set autofocus on the first field // return to check out if need change
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if field in placeholders:
                # Set placeholder to the value in the placeholders dictionary in place 
                self.fields[field].widget.attrs['placeholder'] = placeholders[field]
                # Add a star to the placeholder if the field is required
                if self.fields[field].required:
                    self.fields[field].widget.attrs['placeholder'] += ' *'
            # Remove form field labels
            self.fields[field].label = False
            # Add a CSS class to all fields
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
