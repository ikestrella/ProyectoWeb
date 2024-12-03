from django.db import models


# Create your models here.
class Artista(models.Model):
    imagen = models.ImageField(upload_to='artistas/')  # Cambiado a ImageField
    usuario = models.CharField(max_length=100, unique=True)  # Usuario único
    contrasenia = models.CharField(max_length=128)  # Idealmente usar la autenticación de Django
    acerca = models.CharField(max_length=400)
    correo = models.EmailField(max_length=100, unique=True)
    ncontacto = models.CharField(max_length=15)  # Soporte para diferentes formatos internacionales


    class Meta:
        db_table = 'artista'

    def __str__(self):
        return 'Artista: ' + self.usuario



class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='productos/')  # Cambiado a ImageField
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
    imagen = models.ImageField(upload_to='obras/')  # Para cargar imágenes
    artista = models.ForeignKey(Artista, db_column='artista', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'obra'

    def __str__(self):
        return 'Obra: ' + self.nombre + ' Por: ' + self.artista.usuario
