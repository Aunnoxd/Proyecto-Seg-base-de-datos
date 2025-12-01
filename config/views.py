import os
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone

# --- AQUÍ ESTÁ EL TRUCO: Importamos los modelos desde tu app ---
from bibliotecavirtual.models import Libro, Descarga, Asignacion, Estudiante

# 1. Vista HOME (Ahora sí carga los libros de Oracle)
def home(request):
    libros = Libro.objects.all() # Traemos los libros de la base de datos
    return render(request, 'index.html', {'libros': libros})

# 2. Vista DESCARGAR (La lógica de negocio)
@login_required
def descargar_libro(request, libro_id):
    # Buscamos el libro
    libro = get_object_or_404(Libro, pk=libro_id)
    usuario = request.user

    # Registramos la descarga
    ip = request.META.get('REMOTE_ADDR')
    Descarga.objects.create(usuario=usuario, libro=libro, ip_usuario=ip)

    # Lógica de marcar tarea como completada (Solo si es estudiante)
    if usuario.rol == 'ESTUDIANTE':
        try:
            # Verificamos si tiene perfil de estudiante
            if hasattr(usuario, 'estudiante'):
                tarea = Asignacion.objects.filter(
                    estudiante=usuario.estudiante,
                    libro=libro,
                    estado='PENDIENTE'
                ).first()

                if tarea:
                    tarea.estado = 'COMPLETADO'
                    tarea.metodo_completado = 'DESCARGA'
                    tarea.fecha_completado = timezone.now()
                    tarea.save()
                    print(f"Tarea completada para {usuario.email}")
        except Exception as e:
            print(f"Error en lógica de tarea: {e}")

    # Servir el PDF
    if libro.archivo_pdf:
        filepath = os.path.join(settings.MEDIA_ROOT, libro.archivo_pdf.name)
        if os.path.exists(filepath):
            return FileResponse(open(filepath, 'rb'), as_attachment=True)
    
    raise Http404("El archivo PDF no se encuentra.")