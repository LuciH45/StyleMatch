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
from pydantic import BaseModel, Field
from typing import Literal
from decimal import Decimal
from django.views.decorators.http import require_POST
import json

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

CategoriaProducto = Literal["outfit_completo"]

class ComplementaryProduct(BaseModel):
    """
    Esquema para un producto generado por la IA que complementa el producto principal.
    Variables en inglés para mejor integración backend.
    """
    
    
    complementary_title: str = Field(description="Título corto y creativo del nuevo producto sugerido.")
    
    
    complementary_description: str = Field(description="Descripción detallada del conjunto, materiales y cómo combina con el perfil del cliente.")
    
    
    suggested_price: Decimal = Field(
        description="Precio sugerido en formato decimal (ej: 150000.00 o 80.50). Debe ser razonable para un outfit completo."
    )
    
    
    # Restringida a un solo valor para simplificar
    suggested_category: CategoriaProducto = Field(
        description="Categoría del producto sugerido. DEBE ser 'outfit_completo'."
    )
    
    # quantity (PositiveIntegerField) -> Unidades Iniciales
    # Nuevo campo con valor fijo de 1
    initial_units: int = Field(
        default=1,
        description="Unidades iniciales del producto. DEBE ser siempre 1."
    )

@api_view(["GET"])
def products_api(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)

def style_assistant_view(request, product_id):

    product = Product.objects.get(pk=product_id)
    
    product_title = product.name
    product_description = product.description
    product_category = product.get_category_display()
    product_price = product.price


    user = request.user
    
    if user.is_authenticated:
        
        user_profile = get_object_or_404(UserProfile, user=user)
        
        
        user_skin_color = user_profile.skin_tone 
        user_style_prefs = user_profile.style_preferences

    new_product_prompt = (
        f"Actúa como un diseñador de moda experto y crea un plan de venta para un nuevo producto. "
        f"Tu tarea es diseñar un ÚNICO producto COMPLEMENTARIO que sea un 'Outfit Completo' "
        f"que haga juego perfectamente con el producto principal y el perfil del cliente. "
        f"El precio que sugieras debe ser un precio total y razonable para un conjunto completo."
        f"\n\n--- DATOS DEL PRODUCTO PRINCIPAL ---"
        f"\nNombre: '{product_title}'"
        f"\nCategoría: '{product_category}'"
        f"\nDescripción: '{product_description}'"
        f"\nPrecio: ${product_price}"
        f"\n\n--- PERFIL DEL CLIENTE ---"
        f"\nColor de piel: '{user_skin_color}'"
        f"\nPreferencias de estilo: '{user_style_prefs}'"
        f"\n\n--- FORMATO DE RESPUESTA REQUERIDO ---"
        f"\nGenera la respuesta EXCLUSIVAMENTE como un objeto JSON con las siguientes claves en INGLÉS:"
        f"\n- complementary_title: Título creativo (string)."
        f"\n- complementary_description: Descripción detallada (string)."
        f"\n- suggested_price: Precio decimal (ej: 150000.00)."
        f"\n- suggested_category: DEBE ser 'outfit_completo' (string)."
        f"\n- initial_units: DEBE ser 1 (número entero)."
    )

    generated_product = None
    error_message = None
    raw_ai_response = "No se pudo conectar con la API."
    
    if client:
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=new_product_prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ComplementaryProduct,
                },
            )
            
            # 1. Capturar el texto crudo de la respuesta para debugging
            # La respuesta de la IA (antes de la conversión a JSON)
            raw_ai_response = response.text 
            
            # 2. Intentar la deserialización a objeto Python
            generated_product = json.loads(raw_ai_response)
            
        except json.JSONDecodeError as e:
            # Error específico cuando el texto crudo no es un JSON válido
            error_message = f"Error de Deserialización JSON: La IA devolvió un formato inválido. Detalles: {e}"
        except Exception as e:
            error_message = f"Error Crítico de Deserialización o Red: {e}"
            print(f"ERROR CRÍTICO: {e}")
    
    
    context = {
        'page_title': f'Asistente de Estilo para {product_title}',
        'product': product,
        'product_id': product_id,
        'user_skin_color': user_skin_color,
        'user_style_prefs': user_style_prefs,
        'generated_product': generated_product, 
        'prompt_enviado': new_product_prompt,
        'raw_ai_response': raw_ai_response,
        'error_message': error_message, 
    }
    
    
    return render(request, 'style_assistant_template.html', context)


@require_POST
def save_ai_product(request):
    """
    Guarda los datos recibidos del formulario del producto generado por la IA.
    Añade validación de usuario y de campos críticos.
    """
    
    # ----------------------------------------------
    # 1. VERIFICACIÓN DE AUTENTICACIÓN (CRÍTICO)
    # ----------------------------------------------
    if not request.user.is_authenticated:
        # Usa el sistema de mensajes de Django para notificar al usuario (opcional)
        messages.error(request, "Debes iniciar sesión para añadir productos al inventario.")
        return redirect('inventory_display')
        
    # ----------------------------------------------
    # 2. Recoger datos y convertirlos
    # ----------------------------------------------
    product_name = request.POST.get('name')
    product_description = request.POST.get('description')
    product_category = request.POST.get('category')
    
    # Validación simple de campos críticos (nombre)
    if not product_name or not product_description:
        messages.error(request, "Error: El nombre o la descripción del producto generado están vacíos.")
        return redirect('inventory_display')
        
    # Manejo de cantidad (seguro)
    try:
        product_quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        product_quantity = 1
        
    # Manejo de precio (seguro)
    try:
        product_price = Decimal(request.POST.get('price', '0.00')) 
    except Exception:
        product_price = Decimal('0.00')

    # ----------------------------------------------
    # 3. Crear y guardar el nuevo objeto Product
    # ----------------------------------------------
    try:
        Product.objects.create(
            user=request.user, 
            name=product_name,
            description=product_description,
            category=product_category,
            quantity=product_quantity,
            price=product_price,
        )
        messages.success(request, f"🎉 ¡Producto '{product_name}' añadido exitosamente por la IA!")
        
        # Redirigir
        return redirect('inventory_display')
        
    except Exception as e:
        # Captura errores de la base de datos (ej: restricción UNIQUE para el nombre)
        error_msg = f"Error al guardar el producto en la base de datos: {e}"
        print(error_msg)
        messages.error(request, "Error al guardar el producto. ¿Ya existe un producto con este nombre?")
        
        return redirect('inventory_display')