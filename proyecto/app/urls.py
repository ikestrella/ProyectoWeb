from django.urls import path
#from .views import listar_carreras
from . import views

urlpatterns = [
    path('login/', views.login_artista, name='login'),
    path('perfil/', views.listar_artista_contenido, name='perfil'),
    path('logout/', views.logout_artista, name='logout'),
    path('artistas/', views.listar_artistas,name='inicio'),
    path('perfil/agregar-obra', views.agregar_obra, name='agregarObra')
]

