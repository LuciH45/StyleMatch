from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductEntryForm, RegistrationForm
from .models import Product, UserProfile
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.http import Http404
from django.core.paginator import Paginator

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import ProductSerializer
import os
from google import genai
from google.genai.errors import APIError


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    # Manejar si la clave no está configurada
    client = None


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
            user = form.save()
            login(request, user)
            return redirect('inventory_display')
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@api_view(["GET"])
def products_api(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)

def style_assistant_view(request, product_id):

    product = Product.objects.get(pk=product_id)
    
    product_title = product.name
    product_description = product.description


    user = request.user
    
    if user.is_authenticated:
        
        user_profile = get_object_or_404(UserProfile, user=user)
        
        
        user_skin_color = user_profile.skin_tone 
        user_style_prefs = user_profile.style_preferences

    prompt = (
        f"Actúa como un asistente de estilo personal altamente experimentado. "
        f"Tu objetivo es crear un conjunto ('outfit') completo y armonioso. "
        f"\n\n--- INSTRUCCIONES CLAVE ---"
        f"\n1. El producto principal debe ser el centro del outfit."
        f"\n2. El outfit debe complementar el color de piel y las preferencias del cliente."
        f"\n3. Recomienda 3 prendas adicionales (ej: zapatos, pantalón, chaqueta) y 1 accesorio."
        f"\n\n--- DATOS DEL PRODUCTO PRINCIPAL ---"
        f"\nTítulo: '{product_title}'"
        f"\nDescripción: '{product_description}'"
        f"\n\n--- PERFIL DEL CLIENTE ---"
        f"\nColor de piel: '{user_skin_color}'"
        f"\nPreferencias de estilo: '{user_style_prefs}'"
        f"\n\n--- RECOMENDACIÓN GENERADA ---"
    )

    ia_recommendation = "El Asistente de IA no está disponible."
    
    if client:
        try:
            # 'gemini-2.5-flash' es rápido y bueno para tareas de texto.
            model = 'gemini-2.5-flash' 
            
            response = client.models.generate_content(
                model=model,
                contents=prompt, 
            )
            
            
            ia_recommendation = response.text
            
        except APIError as e:
            # Error específico de la API (ej: clave inválida, cuota excedida)
            ia_recommendation = f"Error de la API de Gemini: {e}. Por favor, revisa tu clave y cuota."
        except Exception as e:
            # Otros errores (ej: problemas de red)
            ia_recommendation = f"Ocurrió un error inesperado al generar la recomendación: {e}"
    
    
    context = {
        'page_title': f'Asistente de Estilo para {product_title}',
        'product': product,
        'product_id': product_id,
        'user_skin_color': user_skin_color,
        'user_style_prefs': user_style_prefs,
        'prompt': prompt, 
        'ia_recommendation': ia_recommendation, 
    }
    
    
    return render(request, 'style_assistant_template.html', context)