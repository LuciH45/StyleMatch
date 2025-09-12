from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductEntryForm
from .models import Product

def home(request):
    return render(request, "home.html")

def inventory_display(request):
    products = Product.objects.all().order_by("name")
    return render(request, "inventory_display.html", {"products": products})

def product_entry(request):
    if request.method == "POST":
        form = ProductEntryForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            category = form.cleaned_data["category"]
            description = form.cleaned_data["description"]
            quantity = form.cleaned_data["quantity"]
            image = form.cleaned_data.get("image")

            # Verificar si ya existe
            product, created = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": category,
                    "description": description,
                    "quantity": quantity,
                    "image": image,
                }
            )
            if not created:
                # Producto ya existía → sumar unidades
                product.quantity += quantity
                if description:
                    product.description = description
                if image:
                    product.image = image
                product.save()
                messages.success(request, f"Se añadieron {quantity} unidades a {product.name}.")
            else:
                messages.success(request, f"Producto {product.name} creado con éxito.")

            return redirect("inventory_display")
    else:
        form = ProductEntryForm()
    return render(request, "product_entry.html", {"form": form})

def add_unit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.quantity += 1
    product.save()
    messages.success(request, f"Se añadió 1 unidad a {product.name}.")
    return redirect("inventory_display")

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    messages.success(request, f"Producto {product.name} eliminado.")
    product.delete()
    return redirect("inventory_display")
