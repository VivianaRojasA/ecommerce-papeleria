from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Orden, ItemOrden
from django.db import transaction

@login_required
def confirmar_compra(request):
    carrito = request.session.get('carrito', {})
    
    if not carrito:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('catalogo')

    try:
        # Usamos un bloque atómico: si algo falla (ej: no hay stock), 
        # no se crea la orden ni se borra el carrito. Todo o nada.
        with transaction.atomic():
            # 1. Crear la Orden principal
            nueva_orden = Orden.objects.create(usuario=request.user)
            
            # 2. Iterar el carrito y crear los items
            for id_prod, detalle in carrito.items():
                producto = Producto.objects.get(id=id_prod)
                
                # Validar stock antes de crear
                if producto.stock >= detalle['cantidad']:
                    ItemOrden.objects.create(
                        orden=nueva_orden,
                        producto=producto,
                        cantidad=detalle['cantidad']
                    )
                    # 3. Restar stock del producto
                    producto.stock -= detalle['cantidad']
                    producto.save()
                else:
                    # Si no hay stock de un producto, lanzamos error para cancelar todo
                    raise Exception(f"No hay suficiente stock de {producto.nombre}")

            # 4. Si todo salió bien, limpiamos el carrito
            request.session['carrito'] = {}
            request.session.modified = True
            
            messages.success(request, f"¡Compra exitosa! Orden #{nueva_orden.id}")
            return render(request, 'tienda/exito.html', {'orden': nueva_orden})

    except Exception as e:
        messages.error(request, str(e))
        return redirect('catalogo')

def catalogo(request):
    productos = Producto.objects.all() # Traemos todos los productos del ORM
    return render(request, 'tienda/catalogo.html', {'productos': productos})

def agregar_al_carrito(request, producto_id):
    # 1. Obtener el carrito de la sesión actual o crear uno vacío si no existe
    carrito = request.session.get('carrito', {})
    
    # 2. Buscamos el producto en la DB para estar seguros de que existe
    producto = get_object_or_404(Producto, id=producto_id)
    id_str = str(producto_id)

    # 3. Actualizamos el diccionario del carrito
    if id_str in carrito:
        carrito[id_str]['cantidad'] += 1
    else:
        # Guardamos datos básicos para no saturar la sesión
        carrito[id_str] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
        }
    
    # 4. Guardamos el carrito de nuevo en la sesión
    request.session['carrito'] = carrito
    
    # IMPORTANTE: Avisar a Django que la sesión cambió para que la guarde
    request.session.modified = True 

    messages.success(request, f"¡{producto.nombre} agregado al carrito!")
    return redirect('catalogo')

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = 0
    items_procesados = []

    for item_id, detalle in carrito.items():
        subtotal = float(detalle['precio']) * detalle['cantidad']
        total += subtotal
        items_procesados.append({
            'id': item_id,
            'nombre': detalle['nombre'],
            'precio': detalle['precio'],
            'cantidad': detalle['cantidad'],
            'subtotal': subtotal
        })

    return render(request, 'tienda/carrito.html', {
        'items': items_procesados,
        'total': total
    })