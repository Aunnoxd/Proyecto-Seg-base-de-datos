# /home/rubi/neoteca_sistema/neoteca/admin.py

from django.contrib import admin
from django.db import connection
from django.contrib import messages
from django.utils.html import format_html
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
        messages.success(request, f" Se promovieron {exitos} estudiantes correctamente.")
    
    if errores:
        detalle_errores = ", ".join(errores)
        messages.warning(request, f" No se pudo promover a algunos: {detalle_errores}")


# --- INLINES (Formularios anidados) ---
class ProfesorInline(admin.StackedInline):
    model = Profesor
    can_delete = False
    verbose_name_plural = 'Perfil de Profesor'
    fk_name = 'id_usuario'
    extra = 0 # No mostrar filas vacías extra

class EstudianteInline(admin.StackedInline):
    model = Estudiante
    can_delete = False
    verbose_name_plural = 'Perfil de Estudiante'
    fk_name = 'id_usuario'
    extra = 0

class TutorInline(admin.StackedInline):
    model = Tutor
    can_delete = False
    verbose_name_plural = 'Perfil de Tutor'
    fk_name = 'id_usuario'
    extra = 0


# --- CONFIGURACIÓN DE ADMINS ---

# 1. USUARIO (Con Lógica Dinámica para Inlines)
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'rol', 'email', 'carnet_identidad')
    list_filter = ('rol',) 
    search_fields = ('nombres', 'apellidos', 'email', 'carnet_identidad')
    ordering = ('apellidos',)
    actions = [promover_estudiantes] 
    
    # --- AQUÍ ESTÁ LA SOLUCIÓN MÁGICA ---
    # En lugar de poner 'inlines = [...]' fijo, usamos esta función.
    def get_inlines(self, request, obj=None):
        """
        Muestra solo el formulario correspondiente al rol seleccionado.
        Si es un usuario nuevo, no muestra nada hasta que se guarde el rol.
        """
        if obj: # Si estamos editando un usuario existente
            if obj.rol == 'PROFESOR':
                return [ProfesorInline]
            elif obj.rol == 'ESTUDIANTE':
                return [EstudianteInline]
            elif obj.rol == 'TUTOR':
                return [TutorInline]
        
        # Si es nuevo o es ADMIN, no mostramos perfiles extra todavía
        return []

    # Opcional: Para que Jazzmin sepa que campos son importantes
    fieldsets = (
        ('Información de Cuenta', {
            'fields': ('email', 'password', 'rol')
        }),
        ('Datos Personales', {
            'fields': ('nombres', 'apellidos', 'carnet_identidad', 'fecha_nacimiento')
        }),
        ('Contacto', {
            'fields': ('direccion', 'telefono')
        }),
    )
    
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
    list_display = ('titulo', 'autor', 'materia', 'grado', 'ver_tiempo')
    list_filter = ('materia', 'grado') 
    search_fields = ('titulo', 'autor')

    def ver_tiempo(self, obj):
        return obj.tiempo_formateado
    
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


# --- GESTIÓN AVANZADA DE PERFILES (TUTOR / ESTUDIANTE) ---

@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_completo', 'codigo_vinculacion', 'ver_estudiantes_a_cargo')
    search_fields = ('id_usuario__nombres', 'id_usuario__apellidos', 'codigo_vinculacion')

    @admin.display(description='Nombre del Tutor', ordering='id_usuario__nombres')
    def get_nombre_completo(self, obj):
        return f"{obj.id_usuario.nombres} {obj.id_usuario.apellidos}"

    @admin.display(description='Estudiantes Vinculados')
    def ver_estudiantes_a_cargo(self, obj):
        hijos = Estudiante.objects.filter(tutor=obj)
        if not hijos.exists():
            return format_html('<span style="color:red;">Sin estudiantes</span>')
        
        lista_html = "<ul>"
        for hijo in hijos:
            nombre_hijo = f"{hijo.id_usuario.nombres} {hijo.id_usuario.apellidos}"
            grado = hijo.grado.nombre if hijo.grado else "Sin Grado"
            lista_html += f"<li><strong>{nombre_hijo}</strong> ({grado})</li>"
        lista_html += "</ul>"
        return format_html(lista_html)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('get_nombre_estudiante', 'get_grado', 'ver_tutor_asignado', 'ver_codigo_tutor')
    list_filter = ('grado', 'tutor')
    search_fields = ('id_usuario__nombres', 'tutor__codigo_vinculacion')

    @admin.display(description='Estudiante', ordering='id_usuario__nombres')
    def get_nombre_estudiante(self, obj):
        return f"{obj.id_usuario.nombres} {obj.id_usuario.apellidos}"

    @admin.display(description='Grado', ordering='grado__nombre')
    def get_grado(self, obj):
        return obj.grado.nombre if obj.grado else "-"

    @admin.display(description='Tutor Responsable')
    def ver_tutor_asignado(self, obj):
        if obj.tutor:
            return f"{obj.tutor.id_usuario.nombres} {obj.tutor.id_usuario.apellidos}"
        return format_html('<span style="color:red;">Sin Tutor</span>')

    @admin.display(description='Código Vinculación')
    def ver_codigo_tutor(self, obj):
        if obj.tutor:
            return format_html(f'<span style="color:green; font-weight:bold;">{obj.tutor.codigo_vinculacion}</span>')
        return "-"


# --- REPORTES (Solo Lectura) ---

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