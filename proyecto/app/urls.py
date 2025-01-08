from django.urls import path
#from .views import listar_carreras
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout_u, name='logout'),
    path('inicio/', views.presentar_inicio,name='inicio'),
    path('perfil/', views.presentar_perfil, name='perfil'),
    path('productos/', views.presentar_productos, name='mostrarProductos'),
    path('obras/', views.presentar_obras, name='mostrarObras'),
    path('perfil/obra/agregar/', views.agregar_obra, name='agregarObra'),
    path('perfil/producto/agregar/', views.agregar_producto, name='agregarProducto')
]

