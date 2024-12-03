from django.urls import path
#from .views import listar_carreras
from . import views

urlpatterns = [
    path('login/', views.login_artista, name='login'),
    path('artista/', views.listar_artista_contenido, name='listar_obras'),
    path('logout/', views.logout_artista, name='logout')
]

