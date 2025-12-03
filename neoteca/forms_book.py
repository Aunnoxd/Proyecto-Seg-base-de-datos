# /home/rubi/neoteca_sistema/neoteca/forms_book.py

from django import forms
from .models import Asignacion, Usuario, Libro, Grado, Materia 
from django.db.models import Q 

# 1. Formulario para Subir Libros
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'categoria', 'grado', 'tiempo_estimado', 'descripcion', 'archivo_pdf']
        
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.TextInput(attrs={'class': 'form-control'}),
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'tiempo_estimado': forms.NumberInput(attrs={
                'class': 'form-control',  # <--- ESTO ES IMPORTANTE PARA QUE SE VEA BIEN
                'placeholder': 'Ej: 60'
            }),
        }

# 2. Formulario para Registrar Tiempo (Estudiante)
class TiempoLecturaForm(forms.Form):
    tiempo_minutos = forms.IntegerField(
        label='Tiempo de Lectura (minutos)',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': 'required'})
    )

# 3. Formulario para Asignar Tarea (Profesor) - ¡ESTE FALTABA!
class AsignacionForm(forms.ModelForm):
    # Campo extra para filtrar visualmente
    grado_filtro = forms.ModelChoiceField(
        queryset=Grado.objects.all(),
        required=False,
        label="Filtrar por Grado (Visual)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Asignacion
        fields = ['materia', 'libro', 'estudiante'] # Incluye MATERIA

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # ESTILOS BOOTSTRAP
        self.fields['libro'].widget.attrs.update({'class': 'form-control'})
        self.fields['estudiante'].widget.attrs.update({'class': 'form-control'})
        self.fields['materia'].widget.attrs.update({'class': 'form-control'})
        
        # --- FILTRO IMPORTANTE ---
        # Solo mostrar Usuarios con rol ESTUDIANTE en el select
        self.fields['estudiante'].queryset = Usuario.objects.filter(rol='ESTUDIANTE').order_by('apellidos')
        
        # Etiquetas
        self.fields['materia'].label = "Materia / Asignatura"
        self.fields['estudiante'].label = "Estudiante"