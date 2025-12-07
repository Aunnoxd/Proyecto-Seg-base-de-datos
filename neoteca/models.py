from django.db import models
from django.utils import timezone
import random
import string

# --- FUNCIÓN AUXILIAR PARA GENERAR CÓDIGO ---
def generar_codigo_tutor():
    # Genera algo como: TUT-4829
    numeros = ''.join(random.choices(string.digits, k=4))
    return f"TUT-{numeros}"

# 1. TABLA GRADO
class Grado(models.Model):
    id_grado = models.AutoField(primary_key=True) 
    nombre = models.CharField(max_length=50, unique=True)
    nivel_jerarquico = models.IntegerField(default=1) 
    
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'GRADO'

# 1.5 TABLA MATERIA
class Materia(models.Model):
    id_materia = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'MATERIA'

# 2. TABLA USUARIO
class Usuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('TUTOR', 'Tutor'),
        ('ESTUDIANTE', 'Estudiante'),
    ]
    
    id_usuario = models.AutoField(primary_key=True)

    email = models.EmailField(unique=True, max_length=100)
    password = models.CharField(max_length=255) 
    carnet_identidad = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    rol = models.CharField(max_length=20, choices=ROLES)
    fecha_registro = models.DateField(default=timezone.now)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    
    # Datos generales
    direccion = models.CharField(max_length=200, null=True, blank=True)
    telefono = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.rol})"
    class Meta:
        db_table = 'USUARIO'

# Categorías
CATEGORIA_CHOICES = [
    ('CIENCIA', 'Ciencia'),
    ('HISTORIA', 'Historia'),
    ('FICCION', 'Ficción'),
    ('LITERATURA', 'Literatura'),
]

# --- TABLAS HIJAS (Datos Específicos) ---

class Profesor(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, db_column='id_usuario')
    especialidad = models.CharField(max_length=100, null=True, blank=True)
    # CORREGIDO: Eliminado salario. Agregado Grado Académico.
    grado_academico = models.CharField(max_length=100, null=True, blank=True) 

    class Meta:
        db_table = 'PROFESOR'

class Tutor(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, db_column='id_usuario')
    codigo_vinculacion = models.CharField(max_length=20, unique=True, default=generar_codigo_tutor)
    # CORREGIDO: Eliminada cuenta bancaria. Agregados datos de contacto cifrables.
    direccion_domicilio = models.CharField(max_length=255, null=True, blank=True)
    telefono_emergencia = models.CharField(max_length=50, null=True, blank=True)
    
    class Meta:
        db_table = 'TUTOR'

class Estudiante(models.Model):
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True, db_column='id_usuario')
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_grado')
    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_tutor')
    datos_medicos = models.CharField(max_length=200, null=True, blank=True) # Encriptado

    class Meta:
        db_table = 'ESTUDIANTE'

# 3. TABLA LIBRO (MODIFICADA CON RELACIÓN A MATERIA)
class Libro(models.Model):
    id_libro = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=200)
    descripcion = models.TextField(help_text='Resumen del libro.', null=True, blank=True)
    
    # YA NO USAMOS CATEGORIA DE TEXTO. AHORA ES UNA RELACIÓN DIRECTA.
    # categoria = models.CharField(...) <--- ESTO SE VA O SE IGNORA
    
    # --- NUEVA RELACIÓN ---
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_materia')
    
    fecha_publicacion = models.DateField(null=True, blank=True)
    archivo_pdf = models.FileField(upload_to='libros/archivos/', help_text='Sube el archivo PDF.')
    
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_grado')
    tiempo_estimado = models.IntegerField(default=0)
    
    # El campo que te daba error antes
    id_usuario_subio = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_usuario_subio')
    
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def tiempo_formateado(self):
        if not self.tiempo_estimado: return "N/A"
        if self.tiempo_estimado < 60: return f"{self.tiempo_estimado} min"
        horas = self.tiempo_estimado // 60
        minutos = self.tiempo_estimado % 60
        return f"{horas} hrs" if minutes == 0 else f"{horas}h {minutos}m"

    def __str__(self):
        return self.titulo
        
    class Meta:
        db_table = 'LIBRO'

# 4. TABLA LEE
class Lee(models.Model):
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_estudiante')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, db_column='id_libro')
    
    fecha_inicio = models.DateTimeField(default=timezone.now)
    tiempo_leido_segundos = models.IntegerField(default=0)

    class Meta:
        db_table = 'LEE'

# 5. TABLA ASIGNACION
class Asignacion(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADO', 'Completado'),
    ]

    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='asignaciones_creadas', db_column='id_profesor')
    estudiante = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tareas_asignadas', db_column='id_estudiante')
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, db_column='id_libro')
    materia = models.ForeignKey(Materia, on_delete=models.SET_NULL, null=True, blank=True, db_column='id_materia')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'ASIGNACION'

# --- REPORTES (Vistas SQL) ---

class RankingLectores(models.Model):
    estudiante = models.CharField(max_length=200, primary_key=True) 
    sesiones_iniciadas = models.IntegerField()
    minutos_totales = models.FloatField()
    class Meta:
        managed = False
        db_table = 'VISTA_RANKING_LECTORES'
    
class ReporteProfesores(models.Model):
    profesor = models.CharField(max_length=200, primary_key=True)
    tareas_asignadas = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'VISTA_CARGA_PROFESORES'
        verbose_name = 'Reporte: Carga de Profesor'
        verbose_name_plural = 'Reporte: Carga de Profesores'

class ReporteSeguridad(models.Model):
    fecha = models.DateTimeField(primary_key=True) 
    usuario_db = models.CharField(max_length=50)
    accion = models.CharField(max_length=50)
    usuario_afectado = models.CharField(max_length=100)
    detalle = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'LOG_AUDITORIA' 
        verbose_name = 'Log de Seguridad'
        verbose_name_plural = 'Logs de Seguridad'

class ReporteTareasPendientes(models.Model):
    id_reporte = models.IntegerField(primary_key=True) 
    tutor = models.CharField(max_length=100)
    estudiante = models.CharField(max_length=100)
    libro_pendiente = models.CharField(max_length=200)
    fecha_asignacion = models.DateTimeField()

    class Meta:
        managed = False 
        db_table = 'REPORTE_TAREAS_PENDIENTES'
        verbose_name = 'Reporte: Tarea Pendiente'
        verbose_name_plural = 'Reporte: Tareas Pendientes'

class VistaUsuariosSegura(models.Model):
    id_usuario = models.IntegerField(primary_key=True)
    nombres = models.CharField(max_length=100)
    rol = models.CharField(max_length=20)
    email_anonimizado = models.CharField(max_length=100)
    carnet_oculto = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'VISTA_USUARIOS_SEGURA'
        verbose_name = 'Auditoría: Usuario Seguro'
        verbose_name_plural = 'Auditoría: Usuarios Seguros'