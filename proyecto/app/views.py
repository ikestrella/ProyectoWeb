from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from .models import Artista, Obra, Producto


def logout_u(request):
    logout(request)
    return redirect('login')


def presentar_perfil(request):
    usuario = request.session.get('usuario')
    artista = Artista.objects.get(usuario=usuario)
    obras = Obra.objects.filter(artista=artista)
    productos = Producto.objects.filter(artista=artista)    
    return render(request, 'pages/perfil/artista.html', {'obras': obras,'productos': productos,'artista':artista})


def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario') 
        contrasenia = request.POST.get('contrasenia')

        try:
            artista = Artista.objects.get(usuario=usuario)
        except:
            return render(request, 'pages/login.html', {'error': 'Usuario no encontrado.'})

        if artista.contrasenia == contrasenia:
                request.session['usuario'] = artista.usuario

                return redirect('perfil')
        else:
            return render(request, 'pages/login.html', {'error': 'Contraseña incorrecta.'})
            
    else:
        return render(request, 'pages/login.html')

def presentar_inicio(request):
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
            
    return render(request, 'pages/perfil/agregar-obra.html')

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
            
    return render(request, 'pages/perfil/agregar-producto.html')

def presentar_productos(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    productos = Producto.objects.filter(artista=artista)
    context = {
        'productos': productos
    }
    return render(request, 'pages/perfil/producto.html', context)

def presentar_obras(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    obras = Obra.objects.filter(artista=artista)
    context = {
        'obras': obras
    }
    return render(request, 'pages/perfil/obra.html', context)
