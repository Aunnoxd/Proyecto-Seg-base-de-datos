# /home/rubi/neoteca_sistema/neoteca/admin.py

from django.contrib import admin
from django.db import connection
from django.contrib import messages
from django.utils.html import format_html # <--- NECESARIO PARA LISTAS HTML
from .models import (
    Grado, Materia, Usuario, Libro, Asignacion, Lee, 
    Profesor, Estudiante, Tutor, 
    RankingLectores, ReporteProfesores, ReporteSeguridad,
    ReporteTareasPendientes, VistaUsuariosSegura
)

# --- ACCIÓN PERSONALIZADA: Promover Estudiantes ---
@admin.action(description='Promover de grado (SP Oracle)')
def promover_estudiantes(modeladmin, request, queryset):
    exitos = 0
    errores = []
    with connection.cursor() as cursor:
        for usuario in queryset:
            try:
                cursor.callproc('promover_estudiante', [usuario.id_usuario])
                exitos += 1
            except Exception as e: 
                errores.append(str(e))
    if exitos: messages.success(request, f" {exitos} promovidos.")
    if errores: messages.warning(request, f" Errores: {errores}")

# --- INLINES ---
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

# --- ADMINS PRINCIPALES ---

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'rol', 'email', 'carnet_identidad')
    list_filter = ('rol',) 
    search_fields = ('nombres', 'apellidos', 'email')
    inlines = [ProfesorInline, EstudianteInline, TutorInline]
    actions = [promover_estudiantes]

# ==============================================================================
# NUEVO: GESTIÓN AVANZADA DE TUTORES (VER HIJOS)
# ==============================================================================
@admin.register(Tutor)
class TutorAdmin(admin.ModelAdmin):
    # Mostramos: Nombre del Tutor, Su Código, y la Lista de Hijos
    list_display = ('get_nombre_completo', 'codigo_vinculacion', 'ver_estudiantes_a_cargo')
    search_fields = ('id_usuario__nombres', 'id_usuario__apellidos', 'codigo_vinculacion')

    # Función para obtener el nombre desde la tabla padre (Usuario)
    @admin.display(description='Nombre del Tutor', ordering='id_usuario__nombres')
    def get_nombre_completo(self, obj):
        return f"{obj.id_usuario.nombres} {obj.id_usuario.apellidos}"

    # Función Mágica: Busca a todos los estudiantes que tengan a este tutor
    @admin.display(description='Estudiantes Vinculados')
    def ver_estudiantes_a_cargo(self, obj):
        # Buscamos en la tabla Estudiante quiénes tienen este ID de tutor
        hijos = Estudiante.objects.filter(tutor=obj)
        
        if not hijos.exists():
            return format_html('<span style="color:red;">Sin estudiantes</span>')
        
        # Armamos una lista HTML bonita
        lista_html = "<ul>"
        for hijo in hijos:
            nombre_hijo = f"{hijo.id_usuario.nombres} {hijo.id_usuario.apellidos}"
            grado = hijo.grado.nombre if hijo.grado else "Sin Grado"
            # Mostramos Nombre y Grado
            lista_html += f"<li><strong>{nombre_hijo}</strong> ({grado})</li>"
        lista_html += "</ul>"
        
        return format_html(lista_html)

# ==============================================================================
# NUEVO: GESTIÓN AVANZADA DE ESTUDIANTES (VER TUTOR)
# ==============================================================================
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

    # Muestra el nombre del Tutor Responsable
    @admin.display(description='Tutor Responsable')
    def ver_tutor_asignado(self, obj):
        if obj.tutor:
            return f"{obj.tutor.id_usuario.nombres} {obj.tutor.id_usuario.apellidos}"
        return format_html('<span style="color:red;">Sin Tutor</span>')

    # Muestra el código del tutor para verificar que coincidan
    @admin.display(description='Código Vinculación')
    def ver_codigo_tutor(self, obj):
        if obj.tutor:
            # Aquí se ve que el código viene del Tutor
            return format_html(f'<span style="color:green; font-weight:bold;">{obj.tutor.codigo_vinculacion}</span>')
        return "-"

# --- RESTO DE ADMINS (Grado, Materia, Libro...) ---
@admin.register(Grado)
class GradoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nivel_jerarquico')

@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'materia', 'grado', 'tiempo_formateado')
    list_filter = ('materia', 'grado')

@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'libro', 'estado', 'created_at')
    list_filter = ('estado', 'created_at')

@admin.register(Lee)
class LeeAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'libro', 'tiempo_leido_segundos')

# --- REPORTES DE SOLO LECTURA ---
@admin.register(RankingLectores)
class RankingLectoresAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'minutos_totales')
    def has_add_permission(self, request): return False

@admin.register(ReporteTareasPendientes)
class ReporteTareasAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'estudiante', 'libro_pendiente', 'fecha_asignacion')
    def has_add_permission(self, request): return False

@admin.register(VistaUsuariosSegura)
class VistaSeguraAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'rol', 'email_anonimizado', 'carnet_oculto')
    def has_add_permission(self, request): return False