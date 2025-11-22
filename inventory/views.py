from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductEntryForm, RegistrationForm
from .models import Product
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.http import Http404
from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ProductSerializer

# Función para verificar si el usuario es un administrador (staff)
def is_staff(user):
    return user.is_staff

def home(request):
    return render(request, "home.html")

@login_required
def inventory_display(request):
    query = request.GET.get("q")
    category = request.GET.get("category")

    products = Product.objects.filter(user=request.user).order_by("name")

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    if category and category != "all":
        products = products.filter(category=category)

    paginator = Paginator(products, 8)  # 8 productos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "inventory_display.html", {
        "products": page_obj,    
        "page_obj": page_obj,    
        "query": query,
        "category": category,
        "categories": Product.CATEGORY_CHOICES,
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    return render(request, "product_detail.html", {"product": product})

# --- Vistas protegidas para administradores ---

@login_required
#@user_passes_test(is_staff)
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
                user=request.user,
                defaults={
                    "category": category,
                    "description": description,
                    "quantity": quantity,
                    "image": image,
                    "user": request.user,
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
    product = get_object_or_404(Product, id=product_id, user=request.user)
    product.quantity += 1
    product.save()
    messages.success(request, f"Se añadió 1 unidad a {product.name}.")
    return redirect("inventory_display")

@login_required
#@user_passes_test(is_staff)
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if product.user != request.user:
        raise Http404("No tienes permiso para eliminar este producto.")
    messages.success(request, f"Producto {product.name} eliminado.")
    product.delete()
    return redirect("inventory_display")


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Guarda el usuario y el perfil (gracias al método save() personalizado en forms.py)
            user = form.save()
            # Opcional: Inicia sesión automáticamente
            login(request, user)
            return redirect('inventory_display') # Redirige a una página de inicio
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@api_view(["GET"])
def products_api(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)