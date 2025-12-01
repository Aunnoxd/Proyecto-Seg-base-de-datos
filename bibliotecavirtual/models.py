from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# --- 1. GESTIÓN DE USUARIOS Y ROLES [cite: 104] ---

class Usuario(AbstractUser):
    # Roles definidos en tu documento
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('TUTOR', 'Tutor'),
        ('ESTUDIANTE', 'Estudiante'),
        ('INVITADO', 'Invitado'),
    )
    
    # Login con email en lugar de username
    email = models.EmailField(unique=True) 
    ci= models.CharField(max_length=20, unique=True, null=True, blank=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='INVITADO')
    fecha_nacimiento = models.DateField(null=True, blank=True)

    # Configuraciones para usar email como login principal
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nombres', 'apellidos'] # username se mantiene interno

    # Campos adicionales para cumplir con names/surnames separados si lo deseas
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.email} - {self.rol}"

# Tabla TUTOR (Hijo) [cite: 16, 17]
class Tutor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    cod = models.CharField(max_length=20, unique=True, help_text="Código que el tutor da al estudiante")

    def __str__(self):
        return f"Tutor: {self.usuario.nombres}"

# Tabla GRADO [cite: 32, 106]
class Grado(models.Model):
    nombre = models.CharField(max_length=50) # Primaria, Secundaria, Promo
    nivel_jerarquico = models.IntegerField(default=1) # Para lógica de permisos

    def __str__(self):
        return self.nombre

# Tabla ESTUDIANTE (Hijo) [cite: 12, 13, 14]
class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    grado = models.ForeignKey(Grado, on_delete=models.SET_NULL, null=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True, related_name='estudiantes')

    def __str__(self):
        return f"Estudiante: {self.usuario.nombres} ({self.grado})"

# Tabla MATERIA [cite: 37, 106]
class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    sigla = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

# --- 2. LIBROS Y LOGICA DE NEGOCIO [cite: 18, 106] ---

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    categoria = models.CharField(max_length=200)
    descripcion = models.TextField()
    archivo_pdf = models.FileField(upload_to='libros_seguros/') # Carpeta protegida
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True) # Para mostrar en la web
    
    # Relaciones
    grado = models.ForeignKey(Grado, on_delete=models.CASCADE)
    subido_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, limit_choices_to={'rol__in': ['ADMIN', 'PROFESOR']})
    
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# Relación LEE (Control de tiempo) [cite: 53, 58]
class Lee(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    tiempo_leido_segundos = models.IntegerField(default=0)
    
    def verificar_cumplimiento(self):
        # Lógica: > 10800 segundos (3 horas)
        if self.tiempo_leido_segundos >= 10800:
            return True
        return False

# Relación DESCARGA [cite: 66, 70]
class Descarga(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_usuario = models.GenericIPAddressField(null=True, blank=True)

# Relación ASIGNACION (Tarea) [cite: 59, 108]
class Asignacion(models.Model):
    profesor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='tareas_asignadas', limit_choices_to={'rol': 'PROFESOR'})
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    
    ESTADOS = (('PENDIENTE', 'Pendiente'), ('COMPLETADO', 'Completado'))
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    
    METODOS = (('DESCARGA', 'Descarga'), ('LECTURA', 'Lectura'), ('MANUAL', 'Manual'))
    metodo_completado = models.CharField(max_length=20, choices=METODOS, null=True, blank=True)
    
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_completado = models.DateTimeField(null=True, blank=True)