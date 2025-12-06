# /home/rubi/neoteca_sistema/neoteca/profesor_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from django.db import connection
# Importamos los modelos necesarios
from .models import Usuario, Lee, Asignacion, Grado, Libro
from .forms_book import AsignacionForm

def mi_clase(request):
    # CORRECCIÓN: Usamos Usuario.objects como pediste.
    # Para ordenar por grado, navegamos la relación: 'estudiante' -> 'grado' -> 'nombre'
    # Usamos select_related('estudiante__grado') para optimizar y evitar lentitud.
    
    estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').select_related('estudiante__grado').order_by('estudiante__grado__nombre', 'apellidos')
    
    progreso_clase = []

    for usuario in estudiantes:
        # 1. Calculamos lecturas
        # (La tabla Lee apunta a Usuario, así que usamos 'usuario' directamente)
        lecturas = Lee.objects.filter(estudiante=usuario)
        
        # Sumamos segundos (usando aggregate o suma simple python)
        total_segundos = sum([l.tiempo_leido_segundos for l in lecturas])
        libros_leidos = lecturas.count()
        
        # 2. Obtener el Grado de forma segura
        # Como estamos en el modelo Padre (Usuario), accedemos al hijo con .estudiante
        try:
            if hasattr(usuario, 'estudiante') and usuario.estudiante.grado:
                nombre_grado = usuario.estudiante.grado.nombre
            else:
                nombre_grado = "Sin Grado"
        except Exception:
            nombre_grado = "Sin Grado"

        # 3. Empaquetamos los datos
        progreso_clase.append({
            'nombres': usuario.nombres,
            'apellidos': usuario.apellidos,
            'carnet': usuario.carnet_identidad,
            'grado': nombre_grado,
            'tiempo_total_minutos': round(total_segundos / 60),
            'libros_leidos': libros_leidos
        })

    contexto = {
        'progreso_clase': progreso_clase,
    }
    return render(request, 'mi_clase.html', contexto)

def asignar_tarea(request):
    # 1. Obtener ID del profesor desde la SESIÓN (Seguridad Oracle)
    profesor_id = request.session.get('usuario_id')
    
    # Validación básica de sesión
    if not profesor_id:
        return redirect('login')

    try:
        profesor_actual = Usuario.objects.get(pk=profesor_id)
    except Usuario.DoesNotExist:
        return redirect('logout')

    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            # 1. Instanciar objeto sin guardar en BD aun
            asignacion = form.save(commit=False)
            
            # 2. Llenar datos faltantes
            asignacion.profesor = profesor_actual
            asignacion.estado = 'PENDIENTE' 
            
            # 3. Guardar en Oracle
            asignacion.save()
            
            # Mensaje de éxito (opcional, pero recomendado)
            # messages.success(request, "Tarea asignada correctamente")
            
            return redirect('mi_clase') 
    else:
        form = AsignacionForm()

    contexto = {
        'form': form,
        'profesor': profesor_actual
    }
    return render(request, 'asignar_tarea.html', contexto)

def asignar_masivo(request):
    # Solo profesores
    if request.session.get('usuario_rol') != 'PROFESOR':
        return redirect('home')

    if request.method == 'POST':
        id_libro = request.POST.get('libro')
        id_grado = request.POST.get('grado')
        descripcion = request.POST.get('descripcion')
        id_profe = request.session.get('usuario_id')

        try:
            # LLAMADA AL PROCEDIMIENTO ALMACENADO
            with connection.cursor() as cursor:
                cursor.callproc('asignar_tarea_grado', [id_profe, id_libro, id_grado, descripcion])
            
            messages.success(request, "Tarea asignada a todo el grado exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al ejecutar procedimiento: {e}")

    # Datos para el formulario
    libros = Libro.objects.all()
    grados = Grado.objects.all()
    return render(request, 'profesor_asignar_masivo.html', {'libros': libros, 'grados': grados})