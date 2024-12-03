from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Artista, Obra, Producto


def logout_artista(request):
    logout(request)  # Elimina la sesión del usuario
    return redirect('login')


def listar_artista_contenido(request):
    # Recuperar el nombre del artista desde la sesión
    usuario = request.session.get('usuario')

    artista = Artista.objects.get(usuario=usuario)
    obras = Obra.objects.filter(artista=artista)
    productos = Producto.objects.filter(artista=artista)
    
    
    return render(request, 'artista.html', {'obras': obras, 
                                            'productos': productos,
                                            'artistafoto':artista.imagen,
                                            'artista': artista.usuario, 
                                            'ncontacto': artista.ncontacto,
                                            'correo': artista.correo,
                                            'acerca': artista.acerca})


def login_artista(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario') 
        contrasenia = request.POST.get('contrasenia')

        try:
            artista = Artista.objects.get(usuario=usuario)
        except:
            return render(request, 'login.html', {'error': 'Usuario no encontrado.'})

        
        if artista.contrasenia == contrasenia:
                # Guardar el usuario en la sesión
                request.session['usuario'] = artista.usuario

                return redirect('listar_obras')
        else:
            return render(request, 'login.html', {'error': 'Contraseña incorrecta.'})
            
    else:
        return render(request, 'login.html')
