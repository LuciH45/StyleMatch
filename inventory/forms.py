from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

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


class RegistrationForm(UserCreationForm):
    # Los campos de username y password ya están en UserCreationForm

    skin_tone = forms.ChoiceField(
        choices=UserProfile.SKIN_TONE_CHOICES,
        label='Tono de Piel'
    )
    style_preferences = forms.ChoiceField(
        choices=UserProfile.STYLE_CHOICES,
        label='Preferencias de Estilo'
    )

    # Método para guardar el usuario y el perfil
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        # 2. Crea y guarda el objeto PerfilUsuario
        profile = UserProfile.objects.create(
            user=user,
            skin_tone=self.cleaned_data.get('skin_tone'),
            style_preferences=self.cleaned_data.get('style_preferences')
        )
        return user
    

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['skin_tone', 'style_preferences']
        
        labels = {
            'skin_tone': 'Tono de Piel',
            'style_preferences': 'Preferencias de Estilo',
        }
        
        widgets = {
            'skin_tone': forms.Select(choices=UserProfile.SKIN_TONE_CHOICES),
            'style_preferences': forms.Select(choices=UserProfile.STYLE_CHOICES),
        }