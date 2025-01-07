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
    
    
    return render(request, 'pages/artista.html', {'obras': obras, 
                                            'productos': productos,
                                            'artista':artista})


def login_artista(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario') 
        contrasenia = request.POST.get('contrasenia')

        try:
            artista = Artista.objects.get(usuario=usuario)
        except:
            return render(request, 'pages/login.html', {'error': 'Usuario no encontrado.'})

        
        if artista.contrasenia == contrasenia:
                # Guardar el usuario en la sesión
                request.session['usuario'] = artista.usuario

                return redirect('perfil')
        else:
            return render(request, 'pages/login.html', {'error': 'Contraseña incorrecta.'})
            
    else:
        return render(request, 'pages/login.html')

def listar_artistas(request):
    artistas = Artista.objects.all()
    productos = Producto.objects.all()
    obras = Obra.objects.all()

    return render(request, 'pages/inicio.html', {
        'artistas': artistas,
        'productos': productos,
        'obras': obras,
    })

def agregar_obra(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            imagen = request.FILES['imagen']
            usuario = request.session.get('usuario')
            artista = Artista.objects.get(usuario=usuario)
            
            obra = Obra(
                nombre=nombre,
                descripcion=descripcion,
                imagen=imagen,
                artista=artista 
            )
            obra.save()
            return redirect('perfil')
        except Exception as e:
            print(f"Error al guardar la obra: {e}")
            
    return render(request, 'pages/agregar-obra.html')

def agregar_producto(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre']
            descripcion = request.POST['descripcion']
            precio = request.POST['precio']
            imagen = request.FILES['imagen']

            usuario = request.session.get('usuario')
            artista = Artista.objects.get(usuario=usuario)
            
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                imagen=imagen,
                artista=artista 
            )
            producto.save()
            return redirect('perfil')
        except Exception as e:
            print(f"Error al guardar la obra: {e}")
            
    return render(request, 'pages/agregar-producto.html')