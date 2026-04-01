from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalogo, name='catalogo'),
    path('agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('confirmar/', views.confirmar_compra, name='confirmar_compra'),
]