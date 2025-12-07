# /home/rubi/neoteca_sistema/neoteca/tutor_views.py

from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from .models import Tutor, Estudiante, Lee, Asignacion, Usuario

def panel_tutor(request):
    # 1. Seguridad
    usuario_id = request.session.get('usuario_id')
    rol = request.session.get('usuario_rol')

    if not usuario_id or rol != 'TUTOR':
        return redirect('login')

    try:
        # 2. Obtener el Tutor
        tutor_actual = Tutor.objects.get(id_usuario=usuario_id)
        
        
        # 3. Buscar Estudiantes (Pupilos)
        pupilos = Estudiante.objects.filter(tutor=tutor_actual).select_related('id_usuario', 'grado')
        
        resumen_progreso = []

        for pupilo in pupilos:
            usuario_hijo = pupilo.id_usuario
            
            # --- A. INFORMACIÓN DE LECTURA (TIEMPO) ---
            lecturas = Lee.objects.filter(estudiante=usuario_hijo)
            total_segundos = lecturas.aggregate(Sum('tiempo_leido_segundos'))['tiempo_leido_segundos__sum'] or 0
            
            # Formatear tiempo
            minutos = round(total_segundos / 60)
            if minutos < 60:
                tiempo_texto = f"{minutos} min"
            else:
                horas = minutos // 60
                rem = minutos % 60
                tiempo_texto = f"{horas}h {rem}m"

            # --- B. INFORMACIÓN DE TAREAS (ASIGNACIONES) ---
            # Contamos cuántas tareas tiene en total y cuántas completadas
            stats_tareas = Asignacion.objects.filter(estudiante=usuario_hijo).aggregate(
                total=Count('id'),
                completadas=Count('id', filter=Q(estado='COMPLETADO')),
                pendientes=Count('id', filter=Q(estado='PENDIENTE'))
            )
            
            # Lógica de Estado para el Tutor
            if stats_tareas['total'] == 0:
                estado_general = "Sin Tareas"
                color_estado = "secondary"
                porcentaje_tareas = 0  # <--- AGREGAR ESTO
            elif stats_tareas['pendientes'] == 0:
                estado_general = "¡Todo al Día!"
                color_estado = "success"
                porcentaje_tareas = 100 # <--- AGREGAR ESTO
            else:
                estado_general = f"{stats_tareas['pendientes']} Pendientes"
                color_estado = "warning"
                # <--- AGREGAR CÁLCULO MATEMÁTICO AQUÍ:
                porcentaje_tareas = int((stats_tareas['completadas'] / stats_tareas['total']) * 100)

            resumen_progreso.append({
                'nombres': usuario_hijo.nombres,
                'apellidos': usuario_hijo.apellidos,
                'grado': pupilo.grado.nombre if pupilo.grado else "-",
                'tiempo_texto': tiempo_texto,
                'tareas_total': stats_tareas['total'],
                'tareas_completadas': stats_tareas['completadas'],
                'estado_general': estado_general,
                'color_estado': color_estado,
                'porcentaje': porcentaje_tareas # <--- ENVIAMOS EL DATO LISTO
            })

    except Tutor.DoesNotExist:
        return redirect('logout')

    contexto = {
        'tutor': tutor_actual,
        'pupilos': resumen_progreso
    }
    return render(request, 'panel_tutor.html', contexto)