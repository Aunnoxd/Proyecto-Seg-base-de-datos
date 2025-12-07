from django import forms
from .models import Libro, Asignacion, Grado, Materia

# --- FORMULARIO PARA SUBIR/EDITAR LIBROS ---
# neoteca/forms_book.py

class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        # AGREGAMOS 'portada' A LA LISTA
        fields = ['titulo', 'autor', 'materia', 'grado', 'tiempo_estimado', 'portada', 'archivo_pdf', 'descripcion']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del libro'}),
            'autor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Autor'}),
            'materia': forms.Select(attrs={'class': 'form-control'}),
            'grado': forms.Select(attrs={'class': 'form-control'}),
            'tiempo_estimado': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutos'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            
            # WIDGET PARA LA PORTADA
            'portada': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            
            'archivo_pdf': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }
        labels = {
            'materia': 'Asignatura / Materia',
            'tiempo_estimado': 'Tiempo de Lectura (Minutos)',
            'portada': 'Imagen de Portada (Opcional)'
        }

# --- FORMULARIO PARA ASIGNAR TAREAS ---
class AsignacionForm(forms.ModelForm):
    # Campo extra que NO se guarda en la tabla Asignacion, solo sirve para filtrar en el HTML
    grado_filtro = forms.ModelChoiceField(
        queryset=Grado.objects.all(),
        required=False,
        label="Filtrar Grado (Visual)",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_grado_filtro'})
    )

    class Meta:
        model = Asignacion
        fields = ['estudiante', 'libro', 'materia'] # Agregamos materia
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-control'}),
            'libro': forms.Select(attrs={'class': 'form-control'}),
            'materia': forms.Select(attrs={'class': 'form-control'}),
        }

# --- FORMULARIO PARA REGISTRAR TIEMPO (AJAX) ---
class TiempoLecturaForm(forms.Form):
    libro_id = forms.IntegerField(widget=forms.HiddenInput())
    segundos = forms.IntegerField(widget=forms.HiddenInput())