from django.contrib import admin

# Register your models here.
from .models import Artista, Producto, Obra

admin.site.register(Artista)
admin.site.register(Producto)
admin.site.register(Obra)