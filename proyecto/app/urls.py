from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('select-plan/', views.select_plan, name='select_plan'),
    path('logout/', views.logout_u, name='logout'),
    path('', views.presentar_inicio, name='inicio'),
    path('perfil/', views.presentar_perfil, name='perfil'),
    path('perfil/configuracion/', views.configuracion, name='configuracion'),
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
    path('obra/<int:obra_id>/', views.presentar_obra, name='mostrarObra'),
    path('productos/', views.presentar_pagina_productos, name='mostrarPaginaProductos'),
    path('perfil/evento/gestionar/<int:evento_id>/', views.gestionar_participacion, name='gestionarParticipacion'),


    path('carrito/', views.mostrar_carrito, name='mostrar_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:item_id>/<str:accion>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('pago/', views.pago, name='pago'),
    path('procesar_pago/', views.procesar_pago, name='procesar_pago'),

    path('producto/<int:producto_id>/', views.producto_detail, name='producto_detail'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    
    path('comentario/agregar/<str:content_type>/<int:object_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('comentario/editar/<int:comentario_id>/', views.editar_comentario, name='editar_comentario'),
    path('comentario/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
    
    path('administrar/', views.administrarPagina, name='administrarPagina'),
    path('accion-producto/<int:producto_id>/', views.accion_producto, name='accion_Producto'),
    path('accion-obra/<int:obra_id>/', views.accion_obra, name='accion_Obra'),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_Producto'),
    path('eliminar-obra/<int:obra_id>/', views.eliminar_obra, name='eliminar_Obra'),
]