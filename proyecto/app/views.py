import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from .forms import UserRegistrationForm
from .models import Artista, Obra, Producto, Evento, ParticipacionEvento, Carrito, CarritoItem, Comentario
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType

def logout_u(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.contrasenia = form.cleaned_data['contrasenia']
            user.imagen = form.cleaned_data.get('imagen', 'media/artistas/avatar.png')
            user.acerca = form.cleaned_data.get('acerca', 'Sin información')
            user.ncontacto = form.cleaned_data.get('ncontacto', 'Sin número')
            
            user.save()

            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'pages/register.html', {'form': form})

def select_plan(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('register')
    
    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return redirect('register')

    if request.method == 'POST':
        plan = request.POST.get('plan')
        if plan in ['plan1', 'plan2', 'plan3']:
            artista.plan = plan
            artista.save()
            messages.success(request, f'Has actualizado tu plan a {plan}.')
        return redirect('configuracion')
    
    planes_disponibles = [
        {'nombre': 'Plan 1', 'valor': 'plan1'},
        {'nombre': 'Plan 2', 'valor': 'plan2'},
        {'nombre': 'Plan 3', 'valor': 'plan3'}
    ]
    
    context = {
        'artista': artista,
        'planes_disponibles': planes_disponibles,
        'plan_actual': artista.plan
    }
    
    return render(request, 'pages/select_plan.html', context)


def administrarPagina(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login') 

    try:
        artista = Artista.objects.get(usuario=usuario)
        if artista.plan != 'admin':
            return redirect('inicio')
    except Artista.DoesNotExist:
        return redirect('login')

    query = request.GET.get('q', '')

    productos = Producto.objects.order_by('verificacion')
    obras = Obra.objects.order_by('verificacion')

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(artista__usuario__icontains=query)
        )
        obras = obras.filter(
            Q(nombre__icontains=query) | 
            Q(descripcion__icontains=query) | 
            Q(artista__usuario__icontains=query)
        )

    paginator_producto = Paginator(productos, 10)
    paginator_obra = Paginator(obras, 10) 

    page_producto = request.GET.get('page_producto', 1)
    page_obra = request.GET.get('page_obra', 1)

    productos_page = paginator_producto.get_page(page_producto)
    obras_page = paginator_obra.get_page(page_obra)

    query_string = '&q=' + query if query else ''

    context = {
        'productos': productos_page,
        'obras': obras_page,
        'query': query,
        'query_string': query_string,
    }
    return render(request, 'pages/administrar.html', context)

def accion_producto(request, producto_id):
    if request.method == 'POST':
        producto = Producto.objects.get(id=producto_id)
        accion = request.POST.get('accion')

        if accion == 'aceptar':
            producto.verificacion = 'ACEPTADO'
            producto.save()
        elif accion == 'rechazar':
            producto.verificacion = 'RECHAZADO'
            producto.save()

    return redirect('administrarPagina')

def accion_obra(request, obra_id):
    if request.method == 'POST':
        obra = Obra.objects.get(id=obra_id)
        accion = request.POST.get('accion')

        if accion == 'aceptar':
            obra.verificacion = 'ACEPTADO'
            obra.save()
        elif accion == 'rechazar':
            obra.verificacion = 'RECHAZADO'
            obra.save()

    return redirect('administrarPagina')

def eliminar_producto(request, producto_id):
    if request.method == 'POST':
        try:
            producto = Producto.objects.get(id=producto_id)
            producto.delete()
            messages.success(request, 'El producto ha sido eliminado.')
        except Producto.DoesNotExist:
            messages.error(request, 'El producto no existe.')

    return redirect('administrarPagina')

def eliminar_obra(request, obra_id):
    if request.method == 'POST':
        try:
            obra = Obra.objects.get(id=obra_id)
            obra.delete()
            messages.success(request, 'La obra ha sido eliminada.')
        except Obra.DoesNotExist:
            messages.error(request, 'La obra no existe.')

    return redirect('administrarPagina')

def configuracion(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    if request.method == 'POST':
        if 'editar_perfil' in request.POST:
            artista.acerca = request.POST.get('acerca', artista.acerca)
            artista.correo = request.POST.get('correo', artista.correo)
            artista.ncontacto = request.POST.get('ncontacto', artista.ncontacto)
            if 'imagen' in request.FILES:
                artista.imagen = request.FILES['imagen']
            artista.save()
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect('perfil')
        
        elif 'cancelar_plan' in request.POST and artista.plan != 'basico':
            artista.plan = 'basico'
            Obra.objects.filter(artista=artista).delete()
            Producto.objects.filter(artista=artista).delete()
            artista.save()
            messages.success(request, "Plan cancelado y obras eliminadas. Ahora tienes el plan básico.")
        
        elif 'upgradear_plan' in request.POST:
            return redirect('select_plan')

    context = {
        'artista': artista,
        'planes': Artista.PLAN_CHOICES,
        'es_mi_perfil': True
    }
    return render(request, 'pages/perfil/configuracion.html', context)

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
        'es_mi_perfil': artista_logueado == artista if artista_logueado else False,
        'planes': Artista.PLAN_CHOICES 
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
            request.session['plan'] = artista.plan
            return redirect('perfil')
        else:
            return render(request, 'pages/login.html', {'error': 'Contraseña incorrecta.'})
            
    else:
        return render(request, 'pages/login.html')

def presentar_inicio(request):
    artistas = Artista.objects.all().exclude(plan='basico').exclude(plan='admin')[:3]
    productos = Producto.objects.all().filter(verificacion='ACEPTADO')[:4]
    obras = Obra.objects.all().filter(verificacion='ACEPTADO')[:3]

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
            stock = request.POST['stock']

            usuario = request.session.get('usuario')
            artista = Artista.objects.get(usuario=usuario)
            
            producto = Producto(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                stock=stock,
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
            if artista.plan == 'basico':
                return redirect('perfil')
            elif artista.plan == 'plan1':
                return redirect('perfil')
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
        stock = request.POST.get('stock')

        producto.nombre = nombre
        producto.descripcion = descripcion
        producto.precio = precio
        producto.stock = stock
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
            if artista.plan == 'basico':
                return redirect('perfil')
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
        
    eventos_creados = Evento.objects.filter(artista=artista).order_by('-fecha_inicio')

    participaciones = ParticipacionEvento.objects.filter(artista=artista, estado='PARTICIPANDO')
    eventos_participando = Evento.objects.filter(participantes__in=participaciones).order_by('-fecha_inicio')

    eventos = (eventos_creados | eventos_participando).distinct().order_by('-fecha_inicio')
    
    search_query = request.GET.get('q', '')
    if search_query:
        eventos = eventos.filter(Q(titulo__icontains=search_query) | Q(descripcion__icontains=search_query))

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
            'id': evento.id,
            'es_creador': evento.artista_id == artista.id if hasattr(evento, 'artista_id') else False
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




def presentar_artistas(request):
    busqueda = request.GET.get("q")
    artistas = Artista.objects.all().exclude(plan='basico').exclude(plan='admin')

    if busqueda:
        artistas = Artista.objects.filter(
            Q(usuario__icontains=busqueda) |
            Q(correo__icontains=busqueda) |
            Q(ncontacto__icontains=busqueda)
        ).distinct()
    paginator = Paginator(artistas, 6)
    page = request.GET.get('page')

    try:
        artistas_page = paginator.page(page)
    except PageNotAnInteger:
        artistas_page = paginator.page(1)
    except EmptyPage:
        artistas_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/artistas.html', {'artistas': artistas_page})


def presentar_pagina_obras(request):
    busqueda = request.GET.get("q")
    obras = Obra.objects.all().filter(verificacion='ACEPTADO')

    if busqueda:
        obras = Obra.objects.filter(
            Q(titulo__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(artista__usuario__icontains=busqueda)
        ).distinct()

    paginator = Paginator(obras, 6)
    page = request.GET.get('page')

    try:
        obras_page = paginator.page(page)
    except PageNotAnInteger:
        obras_page = paginator.page(1)
    except EmptyPage:
        obras_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/obras.html', {'obras': obras_page})


def presentar_pagina_productos(request):
    busqueda = request.GET.get("q")
    productos = Producto.objects.all().filter(verificacion='ACEPTADO')

    if busqueda:
        productos = Producto.objects.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda) |
            Q(artista__usuario__icontains=busqueda)
        ).distinct()

    paginator = Paginator(productos, 6)
    page = request.GET.get('page')

    try:
        productos_page = paginator.page(page)
    except PageNotAnInteger:
        productos_page = paginator.page(1)
    except EmptyPage:
        productos_page = paginator.page(paginator.num_pages)

    return render(request, 'pages/productos.html', {'productos': productos_page})

from django.contrib.contenttypes.models import ContentType

def gestionar_participacion(request, evento_id):
    usuario = request.session.get('usuario')
    
    try:
        artista = Artista.objects.get(usuario=usuario) if usuario else None
    except Artista.DoesNotExist:
        es_artista = False
        artista = None
    else:
        evento = get_object_or_404(Evento, id=evento_id)
        es_artista = (evento.artista == artista)
        ya_solicitado = ParticipacionEvento.objects.filter(artista=artista, evento=evento).exists() if artista else False

    comentarios = Comentario.objects.filter(content_type=ContentType.objects.get_for_model(Evento), object_id=evento_id)

    if es_artista:
        if request.method == 'POST':
            participante_id = request.POST.get('participante_id')
            accion = request.POST.get('accion')
            
            participante = get_object_or_404(Artista, id=participante_id)
            
            try:
                with transaction.atomic():
                    participacion, created = ParticipacionEvento.objects.get_or_create(
                        artista=participante, 
                        evento=evento, 
                        defaults={'estado': 'EN_ESPERA'}
                    )
                    
                    if accion == 'aceptar':
                        participacion.estado = 'PARTICIPANDO'
                    elif accion == 'rechazar':
                        participacion.estado = 'RECHAZADO'
                    
                    participacion.aceptado_rechazado_en = timezone.now()
                    participacion.save()
                    
                    messages.success(request, f'Participación de {participante.usuario} {accion}da con éxito.')
            except Exception as e:
                messages.error(request, f'Error al {accion} la participación: {str(e)}')
        participaciones = ParticipacionEvento.objects.filter(evento=evento).exclude(estado='RECHAZADO').order_by('-solicitado_en')
    else:
        if request.method == 'POST' and request.POST.get('accion') == 'participar':
            if not usuario:
                return redirect('login') 
            try:
                with transaction.atomic():
                    if artista is None:
                        messages.error(request, 'Debes ser un artista registrado para participar en eventos.')
                    else:
                        participacion, created = ParticipacionEvento.objects.get_or_create(
                            artista=artista,
                            evento=evento,
                            defaults={'estado': 'EN_ESPERA'}
                        )
                        if not created:
                            messages.warning(request, 'Ya has solicitado participar en este evento.')
                        else:
                            messages.success(request, 'Tu solicitud para participar ha sido enviada.')
            except Exception as e:
                messages.error(request, f'Error al solicitar participación: {str(e)}')  
        participaciones = ParticipacionEvento.objects.filter(evento=evento, estado='PARTICIPANDO')

    context = {
        'evento': evento,
        'participaciones': participaciones,
        'es_artista': es_artista,
        'artista': artista,
        'ya_solicitado': ya_solicitado,
        'comentarios': comentarios,
    }
    return render(request, 'pages/perfil/evento.html', context)

def presentar_obra(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    comentarios = Comentario.objects.filter(content_type=ContentType.objects.get_for_model(Obra), object_id=obra_id)
    
    context = {
        'obra': obra,
        'comentarios': comentarios,
    }
    return render(request, 'pages/obra.html', context)

def agregar_comentario(request, content_type, object_id):
    if request.method == 'POST':
        usuario = request.session.get('usuario')
        try:
            autor = Artista.objects.get(usuario=usuario)
        except Artista.DoesNotExist:
            messages.error(request, "Debes iniciar sesión para comentar.")
            return redirect('login')

        contenido = request.POST.get('contenido')
        if contenido:
            modelo = get_object_or_404(ContentType, model=content_type)
            objeto = get_object_or_404(modelo.model_class(), pk=object_id)
            
            comentario = Comentario.objects.create(
                autor=autor,
                contenido=contenido,
                content_type=modelo,
                object_id=object_id
            )
            messages.success(request, "Comentario añadido con éxito.")
            return redirect(objeto.get_absolute_url())
    return redirect('login')

def editar_comentario(request, comentario_id):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, id=comentario_id)
        usuario = request.session.get('usuario')
        if usuario != comentario.autor.usuario:
            messages.error(request, "No puedes editar este comentario.")
            return redirect(comentario.content_object.get_absolute_url())
        
        contenido = request.POST.get('contenido')
        if contenido:
            comentario.contenido = contenido
            comentario.save()
            messages.success(request, "Comentario editado con éxito.")
            return redirect(comentario.content_object.get_absolute_url())
    return redirect('login')

def eliminar_comentario(request, comentario_id):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, id=comentario_id)
        usuario = request.session.get('usuario')
        if usuario != comentario.autor.usuario:
            messages.error(request, "No puedes eliminar este comentario.")
            return redirect(comentario.content_object.get_absolute_url())
        
        objeto = comentario.content_object
        comentario.delete()
        messages.success(request, "Comentario eliminado con éxito.")
        return redirect(objeto.get_absolute_url())
    return redirect('login')

@csrf_exempt
def agregar_al_carrito(request, producto_id):
    usuario = request.session.get('usuario')
    if not usuario:
        messages.error(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect('login')

    producto = get_object_or_404(Producto, id=producto_id)
    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        messages.error(request, 'El artista no existe.')
        return redirect('login')

    if producto.stock < 1:
        messages.error(request, 'Producto sin stock.')
        return redirect('producto_detail', producto_id=producto_id)

    carrito, created = Carrito.objects.get_or_create(usuario=artista)

    cantidad = 1 

    carrito_item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        if carrito_item.cantidad + cantidad > producto.stock:
            messages.error(request, 'Cantidad solicitada supera el stock disponible.')
            return redirect('producto_detail', producto_id=producto_id) 
        carrito_item.cantidad += cantidad
    else:
        carrito_item.cantidad = cantidad
    carrito_item.save()

    producto.stock -= cantidad
    producto.save()

    total_items = sum(item.cantidad for item in carrito.items.all())
    request.session['cart_count'] = total_items

    messages.success(request, 'Producto agregado al carrito con éxito.')
    return redirect('mostrar_carrito')

def producto_detail(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    comentarios = Comentario.objects.filter(content_type=ContentType.objects.get_for_model(Producto), object_id=producto_id).order_by('-fecha_creacion')
    
    if request.method == 'POST':
        comentario_texto = request.POST.get('comentario')
        if comentario_texto:
            usuario = request.session.get('usuario')
            try:
                autor = Artista.objects.get(usuario=usuario)
            except Artista.DoesNotExist:
                messages.error(request, "Debes iniciar sesión para comentar.")
                return redirect('login')
            
            Comentario.objects.create(
                autor=autor,
                contenido=comentario_texto,
                content_type=ContentType.objects.get_for_model(Producto),
                object_id=producto_id
            )
            messages.success(request, "Comentario añadido con éxito.")
            return redirect('producto_detail', producto_id=producto_id)

    context = {
        'producto': producto,
        'comentarios': comentarios,
    }
    return render(request, 'pages/producto.html', context)

def mostrar_carrito(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    carrito, created = Carrito.objects.get_or_create(usuario=artista)
    items = carrito.items.all()
    total = carrito.calcular_total()

    total_items = request.session.get('cart_count', 0)

    context = {
        'carrito': carrito,
        'items': items,
        'total': total,
        'total_items': total_items
    }
    return render(request, 'pages/carrito.html', context)

def checkout(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    carrito = Carrito.objects.get(usuario=artista)
    items = list(carrito.items.all())

    if not items:
        messages.add_message(request, messages.WARNING, 'No puedes proceder al pago sin productos en el carrito.')
        return redirect('mostrar_carrito')

    total = carrito.calcular_total()

    return render(request, 'pages/checkout.html', {'items': items, 'total': total, 'factura': False})

@csrf_exempt
def actualizar_cantidad_carrito(request, item_id, accion):
    usuario = request.session.get('usuario')
    if not usuario:
        return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return JsonResponse({'error': 'El artista no existe'}, status=404)

    carrito_item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=artista)

    if accion == 'incrementar':
        if carrito_item.producto.stock > 0:
            carrito_item.cantidad += 1
            carrito_item.producto.stock -= 1
            
            carrito_item.producto.save()
            carrito_item.save()
        else:
            return JsonResponse({'error': 'Producto sin stock'}, status=400)
    elif accion == 'disminuir':
        if carrito_item.cantidad > 1:
            carrito_item.cantidad -= 1
            carrito_item.producto.stock += 1
            carrito_item.producto.save()
            carrito_item.save()
        else:
            carrito_item.producto.stock += carrito_item.cantidad
            carrito_item.producto.save()
            carrito_item.delete()

    total_items = sum(item.cantidad for item in carrito_item.carrito.items.all())
    total = carrito_item.carrito.calcular_total()
    request.session['cart_count'] = total_items
    
    return redirect('mostrar_carrito')

def procesar_pago(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        numero_tarjeta = request.POST.get('numero_tarjeta')
        fecha_expiracion = request.POST.get('fecha_expiracion')
        cvv = request.POST.get('cvv')

        pago_realizado = True

        if pago_realizado:
            usuario = request.session.get('usuario')
            try:
                artista = Artista.objects.get(usuario=usuario)
            except Artista.DoesNotExist:
                return HttpResponse("El artista no existe.", status=404)

            carrito = Carrito.objects.get(usuario=artista)
            items = list(carrito.items.all())
            total = carrito.calcular_total()
            
            carrito.items.all().delete()
            request.session['cart_count'] = 0
            messages.add_message(request, messages.SUCCESS, 'Pago realizado con éxito y carrito limpiado.')
            return render(request, 'pages/checkout.html', {'items': items, 'total': total, 'factura': True})
        else:
            messages.add_message(request, messages.ERROR, 'Error al procesar el pago. Inténtalo de nuevo.')

    return redirect('checkout')


def pago(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('login')

    try:
        artista = Artista.objects.get(usuario=usuario)
    except Artista.DoesNotExist:
        return HttpResponse("El artista no existe.", status=404)

    carrito = Carrito.objects.get(usuario=artista)
    items = carrito.items.all()
    total = carrito.calcular_total()

    return render(request, 'pages/pago.html', {'items': items, 'total': total})