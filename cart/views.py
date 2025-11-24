from django.shortcuts import render, redirect, get_object_or_404
from inventory.models import Product
from .cart import Cart
from django.http import HttpResponse
from .reporting.report_service import ReportService
from .reporting.pdf_report import PdfReportGenerator
from .reporting.excel_report import ExcelReportGenerator

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product, quantity=1)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart_detail')

def checkout(request):
    """
    Vista muy simple que muestra un formulario de pago simulado (GET)
    y en POST muestra una página de éxito (o redirige).
    """
    cart = Cart(request)
    total = getattr(cart, 'get_total_price', 0)
    # Si el carrito provee un callable, llámalo
    if callable(total):
        total = total()

    if request.method == 'POST':
        # Simulación de pago: intentar vaciar carrito si existe método clear
        try:
            clear_fn = getattr(cart, 'clear', None)
            if callable(clear_fn):
                clear_fn()
        except Exception:
            pass
        return render(request, 'cart/checkout_success.html', {'total': total})
    return render(request, 'cart/checkout.html', {'total': total})

def report_pdf(request):
    cart = Cart(request)
    service = ReportService(PdfReportGenerator())
    content = service.build_report(cart)
    return HttpResponse(content, content_type="text/plain")

def report_excel(request):
    cart = Cart(request)
    service = ReportService(ExcelReportGenerator())
    content = service.build_report(cart)
    return HttpResponse(content, content_type="text/plain")
