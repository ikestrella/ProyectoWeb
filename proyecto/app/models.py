from django.db import models


# Create your models here.
class Artista(models.Model):
    imagen = models.ImageField(upload_to='artistas/')
    usuario = models.CharField(max_length=100, unique=True) 
    contrasenia = models.CharField(max_length=128)
    acerca = models.CharField(max_length=400)
    correo = models.EmailField(max_length=100, unique=True)
    ncontacto = models.CharField(max_length=15)


    class Meta:
        db_table = 'artista'

    def __str__(self):
        return  self.usuario



class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')
    precio = models.IntegerField() 
    descripcion = models.TextField(max_length=200)
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'producto'

    def __str__(self):
        return 'Producto: ' + self.nombre 




class Obra(models.Model):  
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=255)
    imagen = models.ImageField(upload_to='obras/')
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'obra'

    def __str__(self):
        return 'Obra: ' + self.nombre + ' Por: ' + self.artista.usuario


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