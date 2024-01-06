from django import forms
from .widgets import CustomClearableFileInput
from .models import Product 

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
