from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductEntryForm
from .models import Product
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test

# Función para verificar si el usuario es un administrador (staff)
def is_staff(user):
    return user.is_staff

def home(request):
    return render(request, "home.html")
@login_required
def inventory_display(request):
    query = request.GET.get("q")
    category = request.GET.get("category")

    products = Product.objects.all().order_by("name")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category and category != "all":
        products = products.filter(category=category)

    return render(request, "inventory_display.html", {
        "products": products,
        "query": query,
        "category": category,
        "categories": Product.CATEGORY_CHOICES,
    })

# --- Vistas protegidas para administradores ---

@login_required
@user_passes_test(is_staff)
def product_entry(request):
    if request.method == "POST":
        form = ProductEntryForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data["name"]
            category = form.cleaned_data["category"]
            description = form.cleaned_data["description"]
            quantity = form.cleaned_data["quantity"]
            image = form.cleaned_data.get("image")

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

@login_required
@user_passes_test(is_staff)
def add_unit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.quantity += 1
    product.save()
    messages.success(request, f"Se añadió 1 unidad a {product.name}.")
    return redirect("inventory_display")

@login_required
@user_passes_test(is_staff)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    messages.success(request, f"Producto {product.name} eliminado.")
    product.delete()
    return redirect("inventory_display")