from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("blusa", "Blusa"),
        ("pantalon", "Pantalón"),
        ("falda", "Falda"),
        ("vestido", "Vestido"),
        ("calzado", "Calzado"),
        ("accesorio", "Accesorio"),
        ("outfit_completo", "Outfit Completo"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=3, default=0.00)

    def __str__(self):
        return f"{self.name} ({self.category})"


class UserProfile(models.Model):
    SKIN_TONE_CHOICES = [
        ('claro', 'Claro'),
        ('medio', 'Medio'),
        ('oscuro', 'Oscuro'),
    ]

    STYLE_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('deportivo', 'Deportivo'),
        ('bohemio', 'Bohemio'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    
    skin_tone = models.CharField(
        max_length=10, 
        choices=SKIN_TONE_CHOICES,
        default='medio'
    )
    style_preferences = models.CharField(
        max_length=15,
        choices=STYLE_CHOICES,
        default='casual'
    )

    def __str__(self):
        return f'Perfil de {self.user.username}'