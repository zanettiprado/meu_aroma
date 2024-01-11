from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Inventory

class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=99, label='Quantity')


    image = forms.ImageField(label='Image', required=False, widget=CustomClearableFileInput)    

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'image': CustomClearableFileInput(attrs={'class': 'form-control custom-class another-class'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control custom-class another-class'
            
class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['quantity_in_stock', 'quantity_allocated']
        widgets = {
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_allocated': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity_in_stock': 'Quantity in Stock',
            'quantity_allocated': 'Quantity Allocated',
        }

    def clean(self):
        cleaned_data = super().clean()
        quantity_in_stock = cleaned_data.get('quantity_in_stock')
        quantity_allocated = cleaned_data.get('quantity_allocated')

        if quantity_in_stock < 0:
            self.add_error('quantity_in_stock', 'Quantity in stock cannot be negative.')

        if quantity_allocated < 0:
            self.add_error('quantity_allocated', 'Quantity allocated cannot be negative.')
