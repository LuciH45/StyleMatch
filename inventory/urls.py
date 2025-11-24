# inventory/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("inventory/", views.inventory_display, name="inventory_display"),
    path("inventory/entry/", views.product_entry, name="product_entry"),
    path("inventory/add/<int:product_id>/", views.add_unit, name="add_unit"),
    path("inventory/delete/<int:product_id>/", views.delete_product, name="delete_product"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path('register/', views.register_view, name='register'),
    path("api/products/", views.products_api),
    path("style-assistant/<int:product_id>/", views.style_assistant_view, name="style_assistant_for_product"),
    path("save_ai_product/", views.save_ai_product, name="save_ai_product"),
    path("profile/edit/", views.edit_user_profile, name="edit_user_profile"),
    path("aliados/", views.aliados_list, name="aliados_list"),
]