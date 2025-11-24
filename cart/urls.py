from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'),
    path('checkout/', views.checkout, name='cart_checkout'),
    path('report/pdf/', views.report_pdf, name='report_pdf'),
    path('report/excel/', views.report_excel, name='report_excel')
]