from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse  # Asegúrate de que esta importación está presente


# Create your models here.


class Artista(models.Model):
    PLAN_CHOICES = [
        ('basico', 'Básico'),
        ('plan1', 'Plan 1'),
        ('plan2', 'Plan 2'),
        ('plan3', 'Plan 3'),
        ('admin', 'Admin'),
    ]
    imagen = models.ImageField(upload_to='artistas/')
    usuario = models.CharField(max_length=100, unique=True) 
    contrasenia = models.CharField(max_length=128)
    acerca = models.CharField(max_length=400)
    correo = models.EmailField(max_length=100, unique=True)
    ncontacto = models.CharField(max_length=15)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='basico')

    class Meta:
        db_table = 'artista'

    def __str__(self):
        return  self.usuario

#crear clase para los admins para que puedan administrar la pagina(usuario/contrasenia)


class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')
    precio = models.IntegerField() 
    descripcion = models.TextField(max_length=200)
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)
    #verificacion espera/aceptado/rechazado/fueradestock
    #stock

    class Meta:
        db_table = 'producto'

    def __str__(self):
        return 'Producto: ' + self.nombre 




class Obra(models.Model):  
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=255)
    imagen = models.ImageField(upload_to='obras/')
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)
    #verificacion espera/aceptado/rechazado

    class Meta:
        db_table = 'obra'

    def __str__(self):
        return 'Obra: ' + self.nombre + ' Por: ' + self.artista.usuario
    
    def get_absolute_url(self):
        # Usa la importación de 'reverse' aquí
        return reverse('mostrarObra', args=[str(self.id)])


class Evento(models.Model):
    artista = models.ForeignKey(Artista, db_column='artista', on_delete=models.SET_NULL, related_name='eventos', null=True)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='eventos/', null=True, blank=True)  # Añadido
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
        # Cambia 'mostrarEvento' por el nombre correcto de la URL
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
    

#agregar
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
    
    # Relaciones polimórficas para permitir comentarios en diferentes tipos de objetos
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'Comentario por {self.autor.usuario} en {self.content_object}'