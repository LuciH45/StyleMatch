from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ("blusa", "Blusa"),
        ("pantalon", "Pantalón"),
        ("falda", "Falda"),
        ("vestido", "Vestido"),
        ("calzado", "Calzado"),
        ("accesorio", "Accesorio"),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
