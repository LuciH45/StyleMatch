from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth import get_user_model
from inventory.models import Product
from cart.cart import Cart

class CartUnitTests(TestCase):
    def setUp(self):
        # crear un user requerido por Product
        User = get_user_model()
        self.user = User.objects.create_user(username='juancaciguz', password='123')
        # Ajusta aquí otros campos obligatorios si tu modelo Product los tiene (ej: slug, stock...)
        self.prod = Product.objects.create(name='Prueba', price=10.0, user=self.user)
        self.rf = RequestFactory()

    def _get_cart(self):
        req = self.rf.get('/')
        # SessionMiddleware requiere un get_response callable en Django modernos
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(req)
        req.session.save()
        return Cart(req)

    def test_agregar_producto_al_carrito(self):
        cart = self._get_cart()
        # intentar añadir con la firma más común; si falla, intentar alternativa
        try:
            cart.add(self.prod, quantity=2)
        except TypeError:
            try:
                cart.add(self.prod.id, 2)
            except Exception:
                self.fail('No se pudo llamar a cart.add con product o product.id')
        items = list(cart)
        # Buscar item por product o product_id
        found = None
        for it in items:
            p = it.get('product') or it.get('product_obj')
            pid = it.get('product_id') or (p.id if p else None)
            if pid == self.prod.id:
                found = it
                break
        self.assertIsNotNone(found, 'Producto no encontrado en el carrito tras add')
        qty = found.get('quantity') or found.get('qty') or found.get('amount')
        self.assertEqual(qty, 2, 'Cantidad esperada 2 tras agregar')

    def test_quitar_producto_del_carrito(self):
        cart = self._get_cart()
        # agregar primero
        try:
            cart.add(self.prod, quantity=3)
        except TypeError:
            try:
                cart.add(self.prod.id, 3)
            except Exception:
                self.fail('No se pudo llamar a cart.add para preparar el test')
        # intentar remove con variantes comunes
        try:
            cart.remove(self.prod)
        except TypeError:
            try:
                cart.remove(self.prod.id)
            except Exception:
                # intentar método "decrement" si existe
                if hasattr(cart, 'decrement'):
                    cart.decrement(self.prod)
                else:
                    self.fail('No se pudo remover el producto: métodos esperados no existen')
        items = list(cart)
        self.assertFalse(any((it.get('product') and getattr(it.get('product'), 'id', None) == self.prod.id)
                             or (it.get('product_id') == self.prod.id) for it in items),
                         'Producto sigue en carrito después de remove')