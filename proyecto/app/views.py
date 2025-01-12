import json
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from .models import Artista, Obra, Producto, Evento

def logout_u(request):
    logout(request)
    return redirect('login')

def presentar_perfil(request, artista_id=None):
    usuario = request.session.get('usuario')
    if usuario:
        try:
            artista_logueado = Artista.objects.get(usuario=usuario)
        except Artista.DoesNotExist:
            return HttpResponse("El artista no existe.", status=404)
    else:
        artista_logueado = None

    if artista_id:
        artista = get_object_or_404(Artista, id=artista_id)
    else:
        artista = artista_logueado

    obras = Obra.objects.filter(artista=artista)
    productos = Producto.objects.filter(artista=artista)
    
    context = {
        'obras': obras,
        'productos': productos,
        'artista': artista,
        'es_mi_perfil': artista_logueado == artista if artista_logueado else False
    }
    return render(request, 'pages/perfil/artista.html', context)

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

def presentar_productos(request, artista_id=None):
    usuario = request.session.get('usuario')
    if not usuario and not artista_id:
        return redirect('login')

    if artista_id:
        artista = get_object_or_404(Artista, id=artista_id)
    else:
        try:
            artista = Artista.objects.get(usuario=usuario)
        except Artista.DoesNotExist:
            return HttpResponse("El artista no existe.", status=404)

    productos = Producto.objects.filter(artista=artista)
    context = {
        'productos': productos,
        'artista': artista,
        'es_mi_perfil': usuario == artista.usuario if usuario else False
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
        if imagen:
            producto.imagen = imagen
        else:
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

def presentar_obras(request, artista_id=None):
    usuario = request.session.get('usuario')
    if not usuario and not artista_id:
        return redirect('login')

    if artista_id:
        artista = get_object_or_404(Artista, id=artista_id)
    else:
        try:
            artista = Artista.objects.get(usuario=usuario)
        except Artista.DoesNotExist:
            return HttpResponse("El artista no existe.", status=404)

    obras = Obra.objects.filter(artista=artista)
    context = {
        'obras': obras,
        'artista': artista,
        'es_mi_perfil': usuario == artista.usuario if usuario else False
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
        imagen = request.FILES.get('imagen')

        obra.nombre = nombre
        obra.descripcion = descripcion
        if imagen:
            obra.imagen = imagen
        else:
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
    return render(request, 'pages/perfil/obra.html', context)

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



def agregar_evento(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        ubicacion = request.POST.get('ubicacion')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        imagen = request.FILES.get('imagen') 

        if titulo and descripcion and ubicacion and fecha_inicio:
            evento = Evento(
                artista=artista,
                titulo=titulo,
                descripcion=descripcion,
                ubicacion=ubicacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin if fecha_fin else None,
                imagen=imagen 
            )
            evento.save()
            messages.success(request, 'Evento añadido con éxito.')
            return redirect('mostrarEventos')
        else:
            messages.error(request, 'Por favor, complete todos los campos obligatorios.')

    return render(request, 'pages/perfil/agregar_evento.html')

def editar_evento(request, evento_id):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    evento = get_object_or_404(Evento, id=evento_id, artista=artista)

    if request.method == 'POST':
        evento.titulo = request.POST.get('titulo')
        evento.descripcion = request.POST.get('descripcion')
        evento.ubicacion = request.POST.get('ubicacion')
        evento.fecha_inicio = request.POST.get('fecha_inicio')
        nueva_fecha_fin = request.POST.get('fecha_fin')
        if nueva_fecha_fin:
            evento.fecha_fin = nueva_fecha_fin
        
        imagen = request.FILES.get('imagen')
        if imagen:
            evento.imagen = imagen
        
        evento.save()
        messages.success(request, 'Evento actualizado con éxito.')
        return redirect('mostrarEventos')
    else:
        context = {
            'evento': evento,
            'editar': True
        }
        return render(request, 'pages/perfil/eventos.html', context)

def presentar_eventos(request, artista_id=None):
    usuario = request.session.get('usuario')
    if not usuario and not artista_id:
        return redirect('login')

    if artista_id:
        artista = get_object_or_404(Artista, id=artista_id)
    else:
        try:
            artista = Artista.objects.get(usuario=usuario)
        except Artista.DoesNotExist:
            return HttpResponse("El artista no existe.", status=404)

    eventos = Evento.objects.filter(artista=artista).order_by('-fecha_inicio')
    
    search_query = request.GET.get('q', '')
    if search_query:
        eventos = eventos.filter(titulo__icontains=search_query)

    paginator = Paginator(eventos, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    eventos_list = []
    colors = ['red', 'blue', 'green', 'purple', 'orange']
    for index, evento in enumerate(eventos):
        evento_data = {
            'title': evento.titulo,
            'start': evento.fecha_inicio.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': evento.fecha_fin.strftime('%Y-%m-%dT%H:%M:%S') if evento.fecha_fin else None,
            'color': colors[index % len(colors)],
            'description': evento.descripcion,
            'location': evento.ubicacion,
            'id': evento.id
        }
        eventos_list.append(evento_data)
    eventos_json = json.dumps(eventos_list)

    context = {
        'eventos_all': eventos,
        'eventos_json': eventos_json,
        'eventos_page': page_obj,
        'artista': artista,
        'es_mi_perfil': usuario == artista.usuario if usuario else False,
        'search_query': search_query
    }
    return render(request, 'pages/perfil/eventos.html', context)

def eliminar_evento(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    if request.method == 'GET':
        evento_id = request.GET.get('id')
        if evento_id:
            try:
                evento = Evento.objects.get(id=evento_id, artista=artista)
                evento.delete()
                messages.success(request, 'Evento eliminado con éxito.')
            except Evento.DoesNotExist:
                messages.error(request, 'El evento no existe o no pertenece al artista.')
        return redirect('mostrarEventos')
    else:
        return HttpResponse("Método no permitido", status=405)
