# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inventory/", views.inventory_display, name="inventory_display"),
    path("inventory/entry/", views.product_entry, name="product_entry"),
    path("inventory/add/<int:product_id>/", views.add_unit, name="add_unit"),
    path("inventory/delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path('register/', views.register_view, name='register'),
    path("api/products/", views.products_api),
]