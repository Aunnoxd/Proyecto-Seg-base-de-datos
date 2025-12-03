# /home/rubi/neoteca_sistema/neoteca/forms_registry.py

from django import forms
from .models import Grado

class RegistroTutorForm(forms.Form):
    nombres = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}))
    apellidos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo Electrónico'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}))
    carnet = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cédula de Identidad'}))
    
    # Campos específicos de Tutor
    telefono = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}))
    direccion = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}))

class RegistroEstudianteForm(forms.Form):
    nombres = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Estudiante'}))
    apellidos = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Institucional (Opcional)'}), required=False)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Crear Contraseña'}))
    carnet = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'C.I. Estudiante'}), required=False)
    
    grado = forms.ModelChoiceField(
        queryset=Grado.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione Grado Escolar"
    )