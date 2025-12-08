# /home/rubi/neoteca_sistema/neoteca/profesor_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import connection
# Importamos modelos
from .models import Usuario, Lee, Asignacion, Grado, Libro, Materia, Profesor
from .forms_book import AsignacionForm

# --- VISTA 1: MI CLASE (MODIFICADA Y CORREGIDA) ---
def mi_clase(request):
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')
    
    profesor_id = request.session.get('usuario_id')
    try:
        profesor_actual = Profesor.objects.get(id_usuario=profesor_id)
        usuario_profe = Usuario.objects.get(pk=profesor_id)
    except Profesor.DoesNotExist:
        return redirect('logout')

    # 1. Lógica de Progreso (La que ya tenías)
    estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').select_related('estudiante__grado').order_by('estudiante__grado__nombre', 'apellidos')
    progreso_clase = []

    for usuario in estudiantes:
        lecturas = Lee.objects.filter(estudiante=usuario)
        total_segundos = sum([l.tiempo_leido_segundos for l in lecturas])
        libros_leidos = lecturas.count()
        nombre_grado = usuario.estudiante.grado.nombre if hasattr(usuario, 'estudiante') and usuario.estudiante.grado else "Sin Grado"

        progreso_clase.append({
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'id_usuario': usuario.id_usuario,
            'grado': nombre_grado,
            'tiempo_total_minutos': round(total_segundos / 60),
            'libros_leidos': libros_leidos
        })

    # 2. LISTA DE TAREAS (AQUÍ ESTABA EL ERROR)
    # Corregido: Quitamos 'grado' y pusimos 'materia' que sí existe en Asignacion
    lista_tareas = Asignacion.objects.filter(
        profesor=usuario_profe
    ).select_related('estudiante', 'libro', 'materia').order_by('-created_at')[:50]

    contexto = {
        'profesor': profesor_actual,
        'progreso_clase': progreso_clase,
        'lista_tareas': lista_tareas,
    }
    return render(request, 'mi_clase.html', contexto)


# --- VISTA 2: ASIGNAR TAREA (INDIVIDUAL) ---
def asignar_tarea(request):
    profesor_id = request.session.get('usuario_id')
    if not profesor_id: return redirect('login')

    try:
        profesor_actual = Usuario.objects.get(pk=profesor_id)
    except Usuario.DoesNotExist: return redirect('logout')

    # Si viene pre-seleccionado un estudiante desde "Mi Clase"
    estudiante_pre = request.GET.get('estudiante')

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
        # Pre-llenar el formulario si venimos del botón "Asignar" de la tabla
        initial_data = {}
        if estudiante_pre:
            initial_data['estudiante'] = estudiante_pre
        form = AsignacionForm(initial=initial_data)

    # Datos para el formulario inteligente
    lista_estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').select_related('estudiante__grado').order_by('apellidos')
    lista_libros = Libro.objects.all().select_related('materia').order_by('titulo')
    lista_materias = Materia.objects.all().order_by('nombre')

    contexto = {
        'form': form,
        'profesor': profesor_actual,
        'lista_estudiantes': lista_estudiantes,
        'lista_libros': lista_libros,
        'lista_materias': lista_materias,
        'estudiante_pre': int(estudiante_pre) if estudiante_pre else None
    }
    return render(request, 'asignar_tarea.html', contexto)


# --- VISTA 3: ASIGNACIÓN MASIVA ---
def asignar_masivo(request):
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')

    if request.method == 'POST':
        id_libro = request.POST.get('libro')
        id_grado = request.POST.get('grado')
        descripcion = request.POST.get('descripcion')
        id_profe = request.session.get('usuario_id')

        try:
            with connection.cursor() as cursor:
                cursor.callproc('asignar_tarea_grado', [id_profe, id_libro, id_grado, descripcion])
            
            messages.success(request, "¡Tarea asignada a todo el curso exitosamente!")
            return redirect('mi_clase')
            
        except Exception as e:
            messages.error(request, f"Error al ejecutar procedimiento: {e}")

    libros = Libro.objects.all().select_related('grado') 
    grados = Grado.objects.all().order_by('nivel_jerarquico')
    
    return render(request, 'profesor_asignar_masivo.html', {
        'libros': libros, 
        'grados': grados
    })


# --- VISTA 4: ELIMINAR TAREA ---
def eliminar_tarea(request, id_asignacion):
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')

    tarea = get_object_or_404(Asignacion, pk=id_asignacion)

    # Seguridad: Solo el dueño borra
    if tarea.profesor.id_usuario != request.session.get('usuario_id'):
        messages.error(request, "No tienes permiso para borrar esta tarea.")
        return redirect('mi_clase')

    titulo = tarea.libro.titulo
    alumno = tarea.estudiante.nombres
    tarea.delete()

    messages.success(request, f"Tarea '{titulo}' para {alumno} eliminada.")
    return redirect('mi_clase')