from django import forms
from .models import Product

class ProductEntryForm(forms.Form):
    CATEGORY_CHOICES = Product.CATEGORY_CHOICES

    name = forms.CharField(label="Nombre de la prenda", max_length=100)
    category = forms.ChoiceField(label="Categoría", choices=CATEGORY_CHOICES)
    description = forms.CharField(label="Descripción", widget=forms.Textarea, required=False)
    quantity = forms.IntegerField(label="Unidades iniciales", min_value=0)
    image = forms.ImageField(label="Imagen", required=False)
    price = forms.DecimalField(label="Precio", min_value=0, decimal_places=3, max_digits=10, initial=0.00)  # <-- Agregado

    def clean_name(self):
        """
        Si el producto ya existe, no lanzamos error.
        Permitimos añadir stock al existente.
        """
        return self.cleaned_data["name"]
