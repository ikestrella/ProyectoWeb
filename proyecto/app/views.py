from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from .models import Artista, Obra, Producto

def logout_u(request):
    logout(request)
    return redirect('login')

def presentar_perfil(request):
    usuario = request.session.get('usuario')
    artista = Artista.objects.get(usuario=usuario)
    obras = Obra.objects.filter(artista=artista)
    productos = Producto.objects.filter(artista=artista)    
    return render(request, 'pages/perfil/artista.html', {'obras': obras, 'productos': productos, 'artista': artista})

def login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario') 
        contrasenia = request.POST.get('contrasenia')

        try:
            artista = Artista.objects.get(usuario=usuario)
        except:
            return render(request, 'pages/login.html', {'error': 'Usuario no encontrado.'})

        if contrasenia == artista.contrasenia:
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
            print(f"Error al guardar el producto: {e}")
            
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
        'productos': productos,
        'artista': artista
    }
    return render(request, 'pages/perfil/producto.html', context)


def editar_producto(request, producto_id):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    producto = get_object_or_404(Producto, id=producto_id, artista=artista)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        imagen = request.FILES.get('imagen')

        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio = precio
        
        # Handle image upload
        if imagen:
            producto.imagen = imagen
        else:
            # If no image was uploaded, keep the existing one
            messages.add_message(request, messages.WARNING, 'Se mantuvo la imagen actual debido a que no se seleccionó una nueva.')

        try:
            producto.save()
            messages.add_message(request, messages.SUCCESS, 'Producto actualizado con éxito.')
        except Exception as e:
            print("Error saving product:", str(e))
            messages.add_message(request, messages.ERROR, 'Hubo un error al actualizar el producto: ' + str(e))
        
        return redirect('mostrarProductos')

    context = {
        'producto': producto,
        'artista': artista
    }
    return render(request, 'pages/perfil/producto.html', context)


def eliminar_producto(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    if request.method == 'GET':
        producto_id = request.GET.get('id')
        if producto_id:
            try:
                producto = Producto.objects.get(id=producto_id, artista=artista)
                producto.delete()
                messages.add_message(request, messages.SUCCESS, 'Producto eliminado con éxito.')
            except Producto.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'El producto no existe o no pertenece al artista.')
        return redirect('mostrarProductos')
    else:
        return HttpResponse("Método no permitido", status=405)

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
        'obras': obras,
        'artista': artista
    }
    return render(request, 'pages/perfil/obra.html', context)

def editar_obra(request, obra_id):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    obra = get_object_or_404(Obra, id=obra_id, artista=artista)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        imagen = request.FILES.get('imagen')  # Obtener el archivo de imagen si se subió

        obra.nombre = nombre
        obra.descripcion = descripcion
        
        # Handle image upload
        if imagen:
            obra.imagen = imagen  # Asignar la nueva imagen si se proporcionó una
        else:
            # Si no se subió una imagen, mantener la actual
            messages.add_message(request, messages.WARNING, 'Se mantuvo la imagen actual debido a que no se seleccionó una nueva.')

        try:
            obra.save()
            messages.add_message(request, messages.SUCCESS, 'Obra actualizada con éxito.')
        except Exception as e:
            print("Error saving obra:", str(e))
            messages.add_message(request, messages.ERROR, 'Hubo un error al actualizar la obra: ' + str(e))
        
        return redirect('mostrarObras')

    context = {
        'obra': obra,
        'artista': artista
    }
    return render(request, 'pages/perfil/editar_obra.html', context)

def eliminar_obra(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    if request.method == 'GET':
        obra_id = request.GET.get('id')
        if obra_id:
            try:
                obra = Obra.objects.get(id=obra_id, artista=artista)
                obra.delete()
                messages.add_message(request, messages.SUCCESS, 'Obra eliminada con éxito.')
            except Obra.DoesNotExist:
                messages.add_message(request, messages.ERROR, 'La obra no existe o no pertenece al artista.')
        return redirect('mostrarObras')
    else:
        return HttpResponse("Método no permitido", status=405)