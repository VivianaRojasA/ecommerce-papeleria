from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)] # Validación: Precio > 0
    )
    stock = models.IntegerField(
        validators=[MinValueValidator(0)] # Validación: Stock >= 0
    )
    # imagen = models.ImageField(upload_to='productos/', null=True, blank=True) 

    def __str__(self):
        return self.nombre

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    completada = models.BooleanField(default=False)

    def __str__(self):
        return f"Orden {self.id} - {self.usuario.username}"

    @property
    def get_total_carrito(self):
        items = self.itemorden_set.all()
        return sum([item.get_subtotal for item in items])

class ItemOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.IntegerField(
        default=0, 
        validators=[MinValueValidator(1)] # Validación: Cantidad > 0
    )

    @property
    def get_subtotal(self):
        return self.producto.precio * self.cantidad