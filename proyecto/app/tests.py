from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Artista, Producto, Obra, Evento

class ArtistaModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='juanperez', password='clave123')
        self.artista = Artista.objects.create(usuario=self.user.username, contrasenia='clave123', plan='plan1')

    def test_creacion_artista(self):
        self.assertTrue(isinstance(self.artista, Artista))
        self.assertEqual(str(self.artista), self.artista.usuario)

    def test_valor_default_plan(self):
        new_artista = Artista.objects.create(usuario='maria', contrasenia='clave456')
        self.assertEqual(new_artista.plan, 'basico')

class ProductoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='juanperez', password='clave123')
        self.artista = Artista.objects.create(usuario=self.user.username, contrasenia='clave123', plan='plan2')
        self.producto = Producto.objects.create(nombre='Camiseta Artística', descripcion='Camiseta de algodón con diseño exclusivo', precio=25000, stock=50, artista=self.artista, verificacion='EN_ESPERA')

    def test_creacion_producto(self):
        self.assertTrue(isinstance(self.producto, Producto))
        self.assertEqual(str(self.producto), f'Producto: {self.producto.nombre}')

    def test_verificacion_producto(self):
        self.assertEqual(self.producto.verificacion, 'EN_ESPERA')
        self.producto.verificacion = 'ACEPTADO'
        self.producto.save()
        producto_actualizado = Producto.objects.get(id=self.producto.id)
        self.assertEqual(producto_actualizado.verificacion, 'ACEPTADO')

class ObraModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='juanperez', password='clave123')
        self.artista = Artista.objects.create(usuario=self.user.username, contrasenia='clave123', plan='plan1')
        self.obra = Obra.objects.create(nombre='Paisaje Andino', descripcion='Pintura al óleo de los Andes', artista=self.artista, verificacion='EN_ESPERA')

    def test_creacion_obra(self):
        self.assertTrue(isinstance(self.obra, Obra))
        self.assertEqual(str(self.obra), f"Obra: {self.obra.nombre} Por: {self.obra.artista.usuario}")

    def test_verificacion_obra(self):
        self.assertEqual(self.obra.verificacion, 'EN_ESPERA')
        self.obra.verificacion = 'RECHAZADO'
        self.obra.save()
        obra_actualizada = Obra.objects.get(id=self.obra.id)
        self.assertEqual(obra_actualizada.verificacion, 'RECHAZADO')

class EventoModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='juanperez', password='clave123')
        self.artista = Artista.objects.create(usuario=self.user.username, contrasenia='clave123', plan='plan1')
        self.fecha_futura = timezone.now() + timezone.timedelta(days=30)
        self.evento = Evento.objects.create(
            titulo='Exposición de Arte Local',
            descripcion='Exposición de obras de artistas emergentes de la región',
            ubicacion='Galería de Arte Moderna, Quito',
            fecha_inicio=self.fecha_futura,
            artista=self.artista
        )

    def test_creacion_evento(self):
        self.assertTrue(isinstance(self.evento, Evento))
        self.assertEqual(str(self.evento), self.evento.titulo)

    def test_fecha_inicio_evento(self):
        self.assertTrue(self.evento.fecha_inicio >= timezone.now())
        nueva_fecha = timezone.now() + timezone.timedelta(days=60)
        self.evento.fecha_inicio = nueva_fecha
        self.evento.save()
        evento_actualizado = Evento.objects.get(id=self.evento.id)
        self.assertEqual(evento_actualizado.fecha_inicio, nueva_fecha)

    def test_fecha_fin_evento(self):
        evento_con_fin = Evento.objects.create(
            titulo='Taller de Pintura',
            descripcion='Taller intensivo de técnicas de pintura al óleo',
            ubicacion='Centro Cultural, Guayaquil',
            fecha_inicio=self.fecha_futura,
            fecha_fin=self.fecha_futura + timezone.timedelta(days=2),
            artista=self.artista
        )
        self.assertTrue(evento_con_fin.fecha_fin > evento_con_fin.fecha_inicio)

    def test_creado_en_evento(self):
        self.assertAlmostEqual(self.evento.creado_en, timezone.now(), delta=timezone.timedelta(seconds=1))

    def test_actualizado_en_evento(self):
        original_update_time = self.evento.actualizado_en
        self.evento.save()
        self.evento.refresh_from_db()
        self.assertGreater(self.evento.actualizado_en, original_update_time)
        
    def test_imagen_evento(self):
        evento_con_imagen = Evento.objects.create(
            titulo='Concierto de Jazz',
            descripcion='Noche de jazz con artistas locales',
            ubicacion='Teatro Sucre, Cuenca',
            fecha_inicio=self.fecha_futura,
            imagen='eventos/jazz_concert.jpg',
            artista=self.artista
        )
        self.assertEqual(evento_con_imagen.imagen, 'eventos/jazz_concert.jpg')