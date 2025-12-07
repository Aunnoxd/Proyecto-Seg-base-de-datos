# /home/rubi/neoteca_sistema/neoteca/estudiante_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse 
from django.db.models import Q, Sum
import json

# Importamos Modelos
from .models import Libro, Usuario, Estudiante, Lee, Asignacion
# Asegúrate de que el form exista en forms_book.py
from neoteca.forms_book import TiempoLecturaForm

# --- DECORADOR DE SEGURIDAD ---
def solo_estudiantes(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get('usuario_rol') != 'ESTUDIANTE':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

# ----------------------------------------------------------------------
# 1. Catálogo de Libros (Lógica Mixta: Estudiante vs Invitado)
# ----------------------------------------------------------------------
def lista_libros(request):
    usuario_id = request.session.get('usuario_id')
    rol_actual = request.session.get('usuario_rol')
    
    # Variables por defecto
    libros = []
    nombre_grado = "Catálogo General"
    es_invitado = True 
    tiempos_por_libro = {}

    # --- CASO A: ES UN ESTUDIANTE ---
    if usuario_id and rol_actual == 'ESTUDIANTE':
        try:
            perfil_estudiante = Estudiante.objects.select_related('grado').get(id_usuario=usuario_id)
            usuario_padre = Usuario.objects.get(pk=usuario_id)
            
            # Filtros de Grado
            if perfil_estudiante.grado:
                libros = Libro.objects.filter(
                    Q(grado=perfil_estudiante.grado) | Q(grado__isnull=True)
                ).select_related('materia').order_by('-id_libro')
                nombre_grado = f"Catálogo - {perfil_estudiante.grado.nombre}"
            else:
                libros = Libro.objects.filter(grado__isnull=True).select_related('materia').order_by('-id_libro')
                nombre_grado = "Sin Grado Asignado"

            # Calcular tiempos leídos (Sumando si hay múltiples registros)
            # Usamos una consulta agregada para ser más precisos
            lecturas = Lee.objects.filter(estudiante=usuario_padre).values('libro').annotate(total=Sum('tiempo_leido_segundos'))
            tiempos_por_libro = {l['libro']: l['total'] for l in lecturas}
            
            es_invitado = False 

        except Estudiante.DoesNotExist:
            return redirect('logout')

    # --- CASO B: OTROS (Invitado, Profe, Admin) ---
    else:
        libros = Libro.objects.all().select_related('materia').order_by('-id_libro')
        if rol_actual == 'PROFESOR':
            nombre_grado = "Vista Docente"
            es_invitado = False
        elif rol_actual == 'ADMIN':
            nombre_grado = "Vista Administrador"
            es_invitado = False
        else:
            nombre_grado = "Catálogo Público"
            es_invitado = True

    # Asignar minutos a cada libro
    for libro in libros:
        segundos = tiempos_por_libro.get(libro.id_libro, 0)
        libro.minutos_acumulados = round(segundos / 60)

    form = TiempoLecturaForm() 
    
    contexto = {
        'libros': libros,
        'form': form,
        'titulo': nombre_grado,
        'es_invitado': es_invitado,
        'rol_actual': rol_actual
    }
    return render(request, 'lista_libros.html', contexto)

# ----------------------------------------------------------------------
# 2. Mis Tareas (Solo Estudiantes)
# ----------------------------------------------------------------------
@solo_estudiantes
def mis_asignaciones(request):
    usuario_id = request.session.get('usuario_id')
    usuario_padre = get_object_or_404(Usuario, pk=usuario_id)

    asignaciones = Asignacion.objects.filter(
        estudiante=usuario_padre
    ).select_related('libro', 'profesor', 'materia').order_by('-created_at')

    contexto = {
        'asignaciones': asignaciones,
        'titulo': 'Mis Tareas de Lectura'
    }
    return render(request, 'mis_asignaciones.html', contexto)

# ----------------------------------------------------------------------
# 3. Registrar Lectura (MANUAL - DESDE EL MODAL)
# ----------------------------------------------------------------------
@require_POST
@solo_estudiantes
def registrar_lectura(request, libro_id):
    usuario_id = request.session.get('usuario_id')
    usuario_padre = get_object_or_404(Usuario, pk=usuario_id)
    libro = get_object_or_404(Libro, pk=libro_id)

    # Si viene del formulario manual (modal)
    tiempo_minutos = request.POST.get('tiempo_minutos')
    
    if tiempo_minutos:
        segundos = int(tiempo_minutos) * 60
        
        # Crear o actualizar registro
        registro, created = Lee.objects.get_or_create(
            estudiante=usuario_padre,
            libro=libro,
            defaults={'tiempo_leido_segundos': 0, 'fecha_inicio': timezone.now()}
        )
        registro.tiempo_leido_segundos += segundos
        registro.save()

        # --- LÓGICA REEMPLAZO DEL TRIGGER ---
        # Verificar si completó la tarea
        if libro.tiempo_estimado > 0:
            minutos_totales = registro.tiempo_leido_segundos / 60
            if minutos_totales >= libro.tiempo_estimado:
                Asignacion.objects.filter(
                    estudiante=usuario_padre, 
                    libro=libro, 
                    estado='PENDIENTE'
                ).update(estado='COMPLETADO')

    return redirect('mis_asignaciones')

# ----------------------------------------------------------------------
# 4. Visor PDF
# ----------------------------------------------------------------------
def ver_libro_pdf(request, id_libro):
    usuario_id = request.session.get('usuario_id')
    rol_actual = request.session.get('usuario_rol')
    libro = get_object_or_404(Libro, pk=id_libro)
    
    minutos_totales = 0
    
    if usuario_id and rol_actual == 'ESTUDIANTE':
        usuario_padre = Usuario.objects.get(pk=usuario_id)
        # Usamos get_or_create para asegurar que exista registro
        lectura, created = Lee.objects.get_or_create(
            estudiante=usuario_padre,
            libro=libro,
            defaults={'tiempo_leido_segundos': 0, 'fecha_inicio': timezone.now()}
        )
        minutos_totales = round(lectura.tiempo_leido_segundos / 60, 1)

    # IMPORTANTE: Pasamos rol_actual para que el template sepa qué botones mostrar
    contexto = {
        'libro': libro,
        'minutos_totales': minutos_totales,
        'rol_actual': rol_actual 
    }
    # Usamos leer_libro.html si ese es tu archivo principal del visor
    return render(request, 'leer_libro.html', contexto)

# ----------------------------------------------------------------------
# 5. AJAX Timer (REEMPLAZO DEL TRIGGER AQUÍ TAMBIÉN)
# ----------------------------------------------------------------------
@require_POST
def registrar_tiempo_ajax(request):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('usuario_rol')

    if not usuario_id or rol != 'ESTUDIANTE':
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

    try:
        data = json.loads(request.body)
        id_libro = data.get('id_libro') or data.get('libro_id')
        segundos = int(data.get('segundos', 0))
        completado = data.get('completado', False) # Si el JS dice que terminó
        
        usuario_padre = Usuario.objects.get(pk=usuario_id)
        libro = Libro.objects.get(pk=id_libro)

        # Guardar tiempo (Actualizamos el registro existente)
        registro_lee, created = Lee.objects.get_or_create(
            estudiante=usuario_padre,
            libro=libro,
            defaults={'tiempo_leido_segundos': 0, 'fecha_inicio': timezone.now()}
        )
        
        registro_lee.tiempo_leido_segundos += segundos
        registro_lee.save() # Guardamos en Oracle

        mensaje_tarea = "Sin cambios"
        
        # --- LÓGICA DE COMPLETADO (REEMPLAZO DEL TRIGGER) ---
        # 1. Si el JS manda la señal explícita OR
        # 2. Si el tiempo acumulado supera el estimado del libro
        
        tiempo_suficiente = False
        if libro.tiempo_estimado > 0:
             # Convertimos a minutos para comparar
             minutos_leidos = registro_lee.tiempo_leido_segundos / 60
             if minutos_leidos >= libro.tiempo_estimado:
                 tiempo_suficiente = True

        if completado or tiempo_suficiente:
            filas = Asignacion.objects.filter(
                estudiante=usuario_padre, 
                libro=libro, 
                estado='PENDIENTE'
            ).update(estado='COMPLETADO')
            
            if filas > 0: 
                mensaje_tarea = "Tarea COMPLETADA Automáticamente"

        return JsonResponse({
            'status': 'ok', 
            'nuevo_total': registro_lee.tiempo_leido_segundos,
            'mensaje': mensaje_tarea
        })

    except Exception as e:
        print(f" ERROR AJAX: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)