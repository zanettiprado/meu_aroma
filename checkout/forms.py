from django import forms
from .models import Order
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from crispy_forms.bootstrap import InlineField


class OrderForm(forms.ModelForm):
    """
    Form for capturing order information.
    """
    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number', 'street_address1',
            'street_address2', 'town_or_city',
            'county', 'country', 'postcode'
        )

    def __init__(self, *args, **kwargs):
        """
        Initialize the form with placeholders and autofocus.
        """

        super(OrderForm, self).__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'county': 'County, State or Locality',
            'country': 'Country',
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


class CouponApplyForm(forms.Form):
    """
    Form for applying a coupon code.
    """
    code = forms.CharField(label='Coupon Code', max_length=100, required=True)

    def __init__(self, *args, **kwargs):
        super(CouponApplyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            InlineField('code', css_class='input-group mb-2 mr-sm-2'),
            Submit('submit', 'Apply', css_class='btn btn-primary mb-2'),
        )