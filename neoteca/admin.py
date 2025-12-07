# neoteca/admin.py

from django.contrib import admin
from django.db import connection
from django.contrib import messages
from .models import (
    Grado, Materia, Usuario, Libro, Asignacion, Lee, 
    Profesor, Estudiante, Tutor, 
    RankingLectores, ReporteProfesores, ReporteSeguridad,
    ReporteTareasPendientes, VistaUsuariosSegura
)

# --- ACCIÓN PERSONALIZADA: Promover Estudiantes (SP Oracle) ---
@admin.action(description='Promover de grado (SP Oracle)')
def promover_estudiantes(modeladmin, request, queryset):
    exitos = 0
    errores = []

    with connection.cursor() as cursor:
        for usuario in queryset:
            try:
                # Llamada al SP
                cursor.callproc('promover_estudiante', [usuario.id_usuario])
                exitos += 1
            except Exception as e: 
                error_msg = str(e)
                if 'ORA-20016' in error_msg:
                    errores.append(f"{usuario.nombres}: Ya está en el último grado.")
                elif 'ORA-20015' in error_msg:
                    errores.append(f"{usuario.nombres}: No tiene grado asignado.")
                else:
                    errores.append(f"{usuario.nombres}: Error Oracle desconocido.")

    if exitos > 0:
        messages.success(request, f"✅ Se promovieron {exitos} estudiantes correctamente.")
    
    if errores:
        detalle_errores = ", ".join(errores)
        messages.warning(request, f"⚠️ No se pudo promover a algunos: {detalle_errores}")


# --- INLINES (Formularios anidados) ---
class ProfesorInline(admin.StackedInline):
    model = Profesor
    can_delete = False
    verbose_name_plural = 'Perfil de Profesor'

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Perfil de Estudiante'

class TutorInline(admin.StackedInline):
    model = Tutor
    can_delete = False
    verbose_name_plural = 'Perfil de Tutor'


# --- CONFIGURACIÓN DE ADMINS ---

# 1. USUARIO (Con Inlines y Acción)
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'rol', 'email', 'carnet_identidad')
    list_filter = ('rol',) 
    search_fields = ('nombres', 'apellidos', 'email', 'carnet_identidad')
    ordering = ('apellidos',)
    inlines = [ProfesorInline, EstudianteInline, TutorInline]
    actions = [promover_estudiantes] 
    
# 2. GRADO
@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('id_grado', 'nombre', 'nivel_jerarquico')
    search_fields = ('nombre',)
    ordering = ('nivel_jerarquico',)

# 3. MATERIA (NUEVO)
@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('id_materia', 'nombre')
    search_fields = ('nombre',)

# 4. LIBRO (CORREGIDO)
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    # CORRECCIÓN: Cambiamos 'categoria' por 'materia'
    list_display = ('titulo', 'autor', 'materia', 'grado', 'ver_tiempo')
    list_filter = ('materia', 'grado') # Filtramos por materia ahora
    search_fields = ('titulo', 'autor')

    def ver_tiempo(self, obj):
        return obj.tiempo_formateado
    
    ver_tiempo.short_description = 'Tiempo Estimado '
    ver_tiempo.admin_order_field = 'tiempo_estimado'

# 5. ASIGNACION
@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    # Agregamos materia también aquí para verla
    list_display = ('libro', 'estudiante', 'profesor', 'materia', 'estado', 'created_at')
    list_filter = ('estado', 'materia', 'created_at')
    search_fields = ('estudiante__nombres', 'libro__titulo')

# 6. LEE
@admin.register(Lee)
class LeeAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'libro', 'tiempo_leido_segundos', 'fecha_inicio')
    list_filter = ('fecha_inicio',)


# --- REPORTES (Vistas SQL - Solo Lectura) ---

@admin.register(RankingLectores)
class RankingLectoresAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'minutos_totales')
    ordering = ('-minutos_totales',)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(ReporteProfesores)
class ReporteProfesoresAdmin(admin.ModelAdmin):
    list_display = ('profesor', 'tareas_asignadas')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(ReporteSeguridad)
class ReporteSeguridadAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'accion', 'usuario_afectado', 'detalle', 'usuario_db')
    list_filter = ('accion', 'usuario_db')
    ordering = ('-fecha',)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

# Reportes Nuevos (Vistas SQL)
@admin.register(ReporteTareasPendientes)
class ReporteTareasAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'estudiante', 'libro_pendiente', 'fecha_asignacion')
    list_filter = ('tutor', 'fecha_asignacion')
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False

@admin.register(VistaUsuariosSegura)
class VistaSeguraAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombres', 'rol', 'email_anonimizado', 'carnet_oculto')
    list_filter = ('rol',)
    search_fields = ('nombres',)
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False