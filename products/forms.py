from django import forms

class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, label='Quantity')
