from django.contrib import admin

# Register your models here.
from .models import Artista, Producto, Obra, Evento, ParticipacionEvento, Carrito, CarritoItem, Comentario, Venta

admin.site.register(Artista)
admin.site.register(Producto)
admin.site.register(Obra)
admin.site.register(Evento)
admin.site.register(ParticipacionEvento)
admin.site.register(Carrito)
admin.site.register(CarritoItem)
admin.site.register(Comentario)
admin.site.register(Venta)