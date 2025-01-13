from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout_u, name='logout'),
    path('', views.presentar_inicio, name='inicio'),
    path('perfil/', views.presentar_perfil, name='perfil'),
    path('perfil/<int:artista_id>/', views.presentar_perfil, name='perfil'),
    path('perfil/obras/', views.presentar_obras, name='mostrarObras'),
    path('perfil/obras/<int:artista_id>/', views.presentar_obras, name='mostrarObras'),
    path('perfil/obra/agregar/', views.agregar_obra, name='agregarObra'),
    path('perfil/obra/editar/<int:obra_id>/', views.editar_obra, name='editarObra'),
    path('perfil/obra/eliminar/', views.eliminar_obra, name='eliminarObra'),
    path('perfil/productos/', views.presentar_productos, name='mostrarProductos'),
    path('perfil/productos/<int:artista_id>/', views.presentar_productos, name='mostrarProductos'),
    path('perfil/producto/agregar/', views.agregar_producto, name='agregarProducto'),
    path('perfil/producto/editar/<int:producto_id>/', views.editar_producto, name='editarProducto'),
    path('perfil/producto/eliminar/', views.eliminar_producto, name='eliminarProducto'),
    path('perfil/evento/agregar/', views.agregar_evento, name='agregarEvento'),
    path('perfil/evento/editar/<int:evento_id>/', views.editar_evento, name='editarEvento'),
    path('perfil/evento/eliminar/', views.eliminar_evento, name='eliminarEvento'),
    path('perfil/eventos/', views.presentar_eventos, name='mostrarEventos'),
    path('perfil/eventos/<int:artista_id>/', views.presentar_eventos, name='mostrarEventos'),
    path('artistas/', views.presentar_artistas, name='mostrarArtistas'),
    path('obras/', views.presentar_pagina_obras, name='mostrarPaginaObras'),
    path('productos/', views.presentar_pagina_productos, name='mostrarPaginaProductos'),
    path('perfil/evento/gestionar/<int:evento_id>/', views.gestionar_participacion, name='gestionarParticipacion')
]