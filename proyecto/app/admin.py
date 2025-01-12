from django.contrib import admin

# Register your models here.
from .models import Artista, Producto, Obra, Evento

admin.site.register(Artista)
admin.site.register(Producto)
admin.site.register(Obra)
admin.site.register(Evento)