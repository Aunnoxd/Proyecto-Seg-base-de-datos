# /home/rubi/neoteca_sistema/neoteca/profesor_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
# Importamos los modelos necesarios
from .models import Usuario, Lee, Asignacion, Grado, Libro, Materia, Profesor
from .forms_book import AsignacionForm

# --- VISTA 1: MI CLASE (PROGRESO) ---
def mi_clase(request):
    # Verificamos sesión de profesor
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')
    # 1. Obtener datos del profesor para mostrar su perfil
    profesor_actual = Profesor.objects.get(id_usuario=request.session.get('usuario_id'))
    # Traemos estudiantes ordenados por grado y apellido
    estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').select_related('estudiante__grado').order_by('estudiante__grado__nombre', 'apellidos')
    
    progreso_clase = []

    for usuario in estudiantes:
        lecturas = Lee.objects.filter(estudiante=usuario)
        total_segundos = sum([l.tiempo_leido_segundos for l in lecturas])
        libros_leidos = lecturas.count()
        
        # Obtener grado de forma segura
        nombre_grado = "Sin Grado"
        try:
            if hasattr(usuario, 'estudiante') and usuario.estudiante.grado:
                nombre_grado = usuario.estudiante.grado.nombre
        except Exception:
            pass

        progreso_clase.append({
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'carnet': usuario.carnet_identidad,
            'grado': nombre_grado,
            'tiempo_total_minutos': round(total_segundos / 60),
            'libros_leidos': libros_leidos
        })

    contexto = {
        'profesor': profesor_actual,
        'progreso_clase': progreso_clase,
    }
    return render(request, 'mi_clase.html', contexto)

# --- VISTA 2: ASIGNAR TAREA (INDIVIDUAL) ---
def asignar_tarea(request):
    profesor_id = request.session.get('usuario_id')
    
    if not profesor_id: return redirect('login')

    try:
        profesor_actual = Usuario.objects.get(pk=profesor_id)
    except Usuario.DoesNotExist: return redirect('logout')

    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            asignacion = form.save(commit=False)
            asignacion.profesor = profesor_actual
            asignacion.estado = 'PENDIENTE' 
            asignacion.save()
            messages.success(request, "Tarea asignada correctamente.")
            return redirect('mi_clase') 
    else:
        form = AsignacionForm()

    # --- DATOS PARA EL FORMULARIO INTELIGENTE ---
    
    lista_estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').select_related('estudiante__grado').order_by('apellidos')
    
    # CAMBIO AQUÍ: Traemos el libro CON su materia asociada
    lista_libros = Libro.objects.all().select_related('materia').order_by('titulo')
    
    lista_materias = Materia.objects.all().order_by('nombre')

    contexto = {
        'form': form,
        'profesor': profesor_actual,
        'lista_estudiantes': lista_estudiantes,
        'lista_libros': lista_libros,
        'lista_materias': lista_materias
    }
    return render(request, 'asignar_tarea.html', contexto)

# --- VISTA 3: ASIGNACIÓN MASIVA (PROCEDIMIENTO ALMACENADO) ---
def asignar_masivo(request):
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')

    if request.method == 'POST':
        id_libro = request.POST.get('libro')
        id_grado = request.POST.get('grado')
        descripcion = request.POST.get('descripcion')
        id_profe = request.session.get('usuario_id')

        try:
            # Llamada al SP de Oracle
            with connection.cursor() as cursor:
                cursor.callproc('asignar_tarea_grado', [id_profe, id_libro, id_grado, descripcion])
            
            messages.success(request, "¡Tarea asignada a todo el curso exitosamente!")
            return redirect('mi_clase')
            
        except Exception as e:
            messages.error(request, f"Error al ejecutar procedimiento: {e}")

    # Cargar datos para los Dropdowns
    libros = Libro.objects.all().select_related('grado') 
    grados = Grado.objects.all().order_by('nivel_jerarquico')
    
    return render(request, 'profesor_asignar_masivo.html', {
        'libros': libros, 
        'grados': grados
    })