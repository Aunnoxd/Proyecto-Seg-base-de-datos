# /home/rubi/neoteca_sistema/neoteca/forms.py

from django import forms
from .models import Asignacion, Usuario, Libro
from django.db.models import Q # Importamos Q para consultas complejas

class AsignacionForm(forms.ModelForm):
    # Sobreescribimos los campos del modelo para personalizarlos en el formulario
    
    # Campo Estudiante: Muestra solo a los usuarios con rol 'ESTUDIANTE'
    estudiante = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(
            Q(rol='ESTUDIANTE') # Filtra por el rol ESTUDIANTE
        ).order_by('apellidos'),
        label="Estudiante a Asignar"
    )

    # Campo Libro: Muestra todos los libros
    libro = forms.ModelChoiceField(
        queryset=Libro.objects.all().order_by('titulo'),
        label="Libro de Lectura"
    )

    # Campo Opcional para Fecha Límite
    fecha_limite = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha Límite (Opcional)"
    )

    class Meta:
        # Basado en el modelo Asignacion
        model = Asignacion
        # Solo necesitamos estos campos para que el profesor los llene
        fields = ['estudiante', 'libro', 'fecha_limite']
        # Los campos 'profesor' y 'estado' los llenaremos en la vista.