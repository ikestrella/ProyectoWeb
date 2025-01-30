from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse


# Create your models here.


from django.db import models

class Artista(models.Model):
    PLAN_CHOICES = [
        ('basico', 'Básico'),
        ('plan1', 'Plan 1'),
        ('plan2', 'Plan 2'),
        ('plan3', 'Plan 3'),
        ('admin', 'Admin'),
    ]
    
    # Mandatory fields
    usuario = models.CharField(max_length=100, unique=True)
    contrasenia = models.CharField(max_length=128)
    
    # Optional fields with default values where appropriate
    imagen = models.ImageField(upload_to='artistas/', blank=True, null=True, default='artistas/avatar.png')
    acerca = models.CharField(max_length=400, blank=True, null=True)
    correo = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    ncontacto = models.CharField(max_length=15, blank=True, null=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basico')

    class Meta:
        db_table = 'artista'

    def __str__(self):
        return self.usuario


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')
    precio = models.IntegerField()
    descripcion = models.TextField(max_length=200)
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)
    stock = models.PositiveIntegerField(default=0)
    ESTADOS_VERIFICACION = [
        ('EN_ESPERA', 'En Espera'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    verificacion = models.CharField(max_length=20, choices=ESTADOS_VERIFICACION, default='EN_ESPERA')


    class Meta:
        db_table = 'producto'

    def __str__(self):
        return 'Producto: ' + self.nombre 
    
    def get_absolute_url(self):
        
        return reverse('producto_detail', args=[str(self.id)])




class Obra(models.Model):  
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=255)
    imagen = models.ImageField(upload_to='obras/')
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)
    ESTADOS_VERIFICACION = [
        ('EN_ESPERA', 'En Espera'),
        ('ACEPTADO', 'Aceptado'),
        ('RECHAZADO', 'Rechazado'),
    ]
    verificacion = models.CharField(max_length=20, choices=ESTADOS_VERIFICACION, default='EN_ESPERA')


    class Meta:
        db_table = 'obra'

    def __str__(self):
        return 'Obra: ' + self.nombre + ' Por: ' + self.artista.usuario
    
    def get_absolute_url(self):
        return reverse('mostrarObra', args=[str(self.id)])


class Evento(models.Model):
    artista = models.ForeignKey(Artista, db_column='artista', on_delete=models.SET_NULL, related_name='eventos', null=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'evento'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.titulo
    
    def get_absolute_url(self):
        return reverse('gestionarParticipacion', args=[str(self.id)])
    

class ParticipacionEvento(models.Model):
    ESTADOS_PARTICIPACION = [
        ('RECHAZADO', 'Rechazado'),
        ('PARTICIPANDO', 'Participando'),
        ('EN_ESPERA', 'En Espera'),
    ]
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name='participaciones')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='participantes')
    estado = models.CharField(max_length=20, choices=ESTADOS_PARTICIPACION, default='EN_ESPERA')
    solicitado_en = models.DateTimeField(auto_now_add=True)
    aceptado_rechazado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'participacionevento'

    def __str__(self):
        return f'{self.artista.usuario} en {self.evento.titulo} - Estado: {self.get_estado_display()}'
    


class Carrito(models.Model):
    usuario = models.ForeignKey(Artista, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito de {self.usuario.usuario}"

    def calcular_total(self):
        total = sum(item.producto.precio * item.cantidad for item in self.items.all())
        return total

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def subtotal(self):
        return self.producto.precio * self.cantidad
    
class Comentario(models.Model):
    autor = models.ForeignKey(Artista, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Comentario por {self.autor.usuario} en {self.content_object}'
    
class Venta(models.Model):
    usuario = models.ForeignKey(Artista, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_compra = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'venta'
        
    def __str__(self):
        return f"Venta de {self.cantidad} {self.producto.nombre} por {self.usuario.usuario}"