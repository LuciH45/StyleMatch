from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import models

# Ajusta esta importación al lugar donde esté tu modelo Product.
# Ejemplos comunes:
# from shop.models import Product
# from products.models import Product
from inventory.models import Product

CART_SESSION_ID = getattr(settings, 'CART_SESSION_ID', 'cart')

class Cart:
    """
    Carrito almacenado en la sesión.
    Guarda items como:
    { "<product_id>": {"quantity": int, "price": "12.50", "name": "Nombre"} }
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not cart:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        if product is None:
            raise ValueError("Importación de Product incorrecta. Ajusta la ruta del import.")
        pid = str(product.id)
        price = str(product.price)  # guardamos como string (serializable)
        if pid not in self.cart:
            self.cart[pid] = {'quantity': 0, 'price': price, 'name': getattr(product, 'name', '')}
        if update_quantity:
            self.cart[pid]['quantity'] = int(quantity)
        else:
            self.cart[pid]['quantity'] += int(quantity)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self.save()

    def clear(self):
        self.session[CART_SESSION_ID] = {}
        self.save()

    def __iter__(self):
        product_ids = list(self.cart.keys())
        if Product is None:
            for pid, item in self.cart.items():
                price = Decimal(item['price'])
                qty = int(item['quantity'])
                yield {
                    'product': None,
                    'id': pid,
                    'name': item.get('name', ''),
                    'price': price.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP),  # <-- 3 decimales
                    'quantity': qty,
                    'total_price': (price * qty).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)  # <-- 3 decimales
                }
            return

        products = Product.objects.filter(id__in=product_ids)
        prod_map = {str(p.id): p for p in products}
        for pid, item in self.cart.items():
            product = prod_map.get(pid)
            price = Decimal(item['price'])
            qty = int(item['quantity'])
            yield {
                'product': product,
                'id': pid,
                'name': item.get('name') or (product.name if product else ''),
                'price': price.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP),  # <-- 3 decimales
                'quantity': qty,
                'total_price': (price * qty).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)  # <-- 3 decimales
            }

    def __len__(self):
        """Cantidad total de unidades en el carrito (suma de cantidades)."""
        return sum(int(item['quantity']) for item in self.cart.values())

    def get_total_price(self):
        total = sum(Decimal(item['price']) * int(item['quantity']) for item in self.cart.values())
        return total.quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)  # <-- 3 decimales

    def get_distinct_items_count(self):
        return len(self.cart)

    def as_dict(self):
        """
        Representación serializable para devolver por JSON.
        Convierte Decimals a str para evitar problemas de serialización.
        """
        items = []
        for item in self:
            items.append({
                'product_id': item['id'],
                'name': item['name'],
                'price': str(item['price']),
                'quantity': item['quantity'],
                'total_price': str(item['total_price']),
            })
        return {
            'items': items,
            'total_price': str(self.get_total_price()),
            'total_quantity': self.__len__(),
            'distinct_items': self.get_distinct_items_count()
        }

