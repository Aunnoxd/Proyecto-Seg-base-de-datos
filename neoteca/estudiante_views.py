# /home/rubi/neoteca_sistema/neoteca/estudiante_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.http import JsonResponse 
from django.db.models import Q
import json

# Importamos Modelos
from .models import Libro, Usuario, Estudiante, Lee, Asignacion
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
            
            if perfil_estudiante.grado:
                libros = Libro.objects.filter(
                    Q(grado=perfil_estudiante.grado) | Q(grado__isnull=True)
                ).order_by('-id_libro')
                nombre_grado = f"Catálogo - {perfil_estudiante.grado.nombre}"
            else:
                libros = Libro.objects.filter(grado__isnull=True).order_by('-id_libro')
                nombre_grado = "Sin Grado Asignado"

            # Calcular tiempos leídos
            lecturas = Lee.objects.filter(estudiante=usuario_padre)
            tiempos_por_libro = {lee.libro.id_libro: lee.tiempo_leido_segundos for lee in lecturas}
            
            es_invitado = False 

        except Estudiante.DoesNotExist:
            return redirect('logout')

    # --- CASO B: OTROS (Invitado, Profe, Admin) ---
    else:
        libros = Libro.objects.all().order_by('-id_libro')
        if rol_actual == 'PROFESOR':
            nombre_grado = "Vista Docente"
        elif rol_actual == 'ADMIN':
            nombre_grado = "Vista Administrador"
        else:
            nombre_grado = "Catálogo Público"

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
# 3. Registrar Lectura (VISTA CLÁSICA QUE FALTABA)
# ----------------------------------------------------------------------
# Esta es la función que te faltaba y causaba el error en urls.py
@require_POST
@solo_estudiantes
def registrar_lectura(request, libro_id):
    usuario_id = request.session.get('usuario_id')
    usuario_padre = get_object_or_404(Usuario, pk=usuario_id)
    libro = get_object_or_404(Libro, pk=libro_id)

    form = TiempoLecturaForm(request.POST)
    if form.is_valid():
        tiempo_minutos = form.cleaned_data['tiempo_minutos']
        tiempo_segundos = tiempo_minutos * 60

        Lee.objects.create(
            estudiante=usuario_padre,
            libro=libro,
            fecha_inicio=timezone.now(), 
            tiempo_leido_segundos=tiempo_segundos
        )
        return redirect('lista_libros') 
    
    return redirect('lista_libros')

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

    contexto = {
        'libro': libro,
        'minutos_totales': minutos_totales,
    }
    return render(request, 'ver_pdf_timer.html', contexto)

# ----------------------------------------------------------------------
# 5. AJAX Timer (VISTA MODERNA PARA EL VISOR)
# ----------------------------------------------------------------------
@require_POST
def registrar_tiempo_ajax(request):
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('usuario_rol')

    if not usuario_id or rol != 'ESTUDIANTE':
        return JsonResponse({'status': 'error', 'message': 'No autorizado'}, status=403)

    try:
        data = json.loads(request.body)
        id_libro = data.get('id_libro')
        segundos = int(data.get('segundos', 0))
        completado = data.get('completado', False)
        
        # Logs en consola para depurar
        print(f" AJAX: Libro {id_libro} | +{segundos}s | Completado: {completado}")

        usuario_padre = Usuario.objects.get(pk=usuario_id)
        libro = Libro.objects.get(pk=id_libro)

        # Guardar tiempo
        registro_lee, created = Lee.objects.get_or_create(
            estudiante=usuario_padre,
            libro=libro,
            # Agrupar por fecha de inicio hoy
            fecha_inicio__date=timezone.now().date(),
            defaults={'tiempo_leido_segundos': 0, 'fecha_inicio': timezone.now()}
        )
        
        registro_lee.tiempo_leido_segundos += segundos
        registro_lee.save()

        mensaje_tarea = "Sin cambios en tareas"
        
        # Marcar tarea como completada si aplica
        if completado:
            filas = Asignacion.objects.filter(
                estudiante=usuario_padre, 
                libro=libro, 
                estado='PENDIENTE'
            ).update(estado='COMPLETADO')
            
            if filas > 0: 
                mensaje_tarea = "Tarea COMPLETADA"
            else:
                mensaje_tarea = " No había tarea pendiente"

        print(f"GUARDADO OK. {mensaje_tarea}")

        return JsonResponse({
            'status': 'ok', 
            'nuevo_total': registro_lee.tiempo_leido_segundos
        })

    except Exception as e:
        print(f" ERROR: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)