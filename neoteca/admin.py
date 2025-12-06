# neoteca/admin.py

from django.contrib import admin
from django.db import connection, DatabaseError
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
            except Exception as e: # Capturamos cualquier error para no romper el admin
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
    actions = [promover_estudiantes] # Aquí registramos la acción
    class Media:
        js = ('js/admin_roles.js',) # Carga nuestro script mágico
# 2. GRADO
@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('id_grado', 'nombre', 'nivel_jerarquico')
    search_fields = ('nombre',)
    ordering = ('nivel_jerarquico',)

# 3. MATERIA
@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('id_materia', 'nombre')
    search_fields = ('nombre',)

# 4. LIBRO
@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'grado', 'ver_tiempo')
    list_filter = ('categoria', 'grado')
    search_fields = ('titulo', 'autor')

    def ver_tiempo(self, obj):
        # Llamamos a la propiedad que creamos en models.py
        return obj.tiempo_formateado
    
    # Esto pone el título bonito a la columna
    ver_tiempo.short_description = 'Tiempo Estimado '
    ver_tiempo.admin_order_field = 'tiempo_estimado'

# 5. ASIGNACION
@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
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

@admin.register(ReporteTareasPendientes)
class ReporteTareasAdmin(admin.ModelAdmin):
    # Usamos 'fecha_asignacion' porque así le pusimos en el modelo
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