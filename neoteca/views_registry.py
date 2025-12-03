# /home/rubi/neoteca_sistema/neoteca/views_registry.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .forms_registry import RegistroTutorForm, RegistroEstudianteForm
from .models import Tutor, Estudiante, Usuario, Grado

# --- 1. REGISTRO PÚBLICO DE TUTOR ---
def registro_tutor(request):
    if request.method == 'POST':
        form = RegistroTutorForm(request.POST)
        if form.is_valid():
            try:
                # Usamos el SP de Oracle para crear el Usuario Base + Tutor
                # Respetando la seguridad del informe
                with connection.cursor() as cursor:
                    # Parámetros: email, pass, nombres, apellidos, rol, carnet
                    cursor.callproc('crear_usuario_seguro', [
                        form.cleaned_data['email'],
                        form.cleaned_data['password'],
                        form.cleaned_data['nombres'],
                        form.cleaned_data['apellidos'],
                        'TUTOR', # Rol fijo
                        form.cleaned_data['carnet']
                    ])
                
                # OJO: El SP crea el usuario y la fila en TUTOR.
                # Si tu SP solo crea USUARIO, tendríamos que insertar en TUTOR manual aquí.
                # Asumiremos que el SP hace el trabajo completo o insertamos los extras:
                
                # Actualizar datos extra del tutor (telefono, dirección) usando Django
                # (Ya que el usuario ya existe gracias al SP)
                usuario_nuevo = Usuario.objects.get(email=form.cleaned_data['email'])
                usuario_nuevo.telefono = form.cleaned_data['telefono']
                usuario_nuevo.direccion = form.cleaned_data['direccion']
                usuario_nuevo.save()
                
                # Crear la instancia en tabla hija si el SP no lo hizo
                Tutor.objects.get_or_create(id_usuario=usuario_nuevo)

                messages.success(request, "¡Cuenta creada! Inicie sesión.")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error al registrar en Oracle: {e}")
    else:
        form = RegistroTutorForm()

    return render(request, 'registro_tutor.html', {'form': form})

# --- 2. REGISTRO DE ESTUDIANTE (POR EL TUTOR) ---
def registrar_estudiante_por_tutor(request):
    # Seguridad: Solo Tutores logueados
    if request.session.get('usuario_rol') != 'TUTOR':
        return redirect('home')

    if request.method == 'POST':
        form = RegistroEstudianteForm(request.POST)
        if form.is_valid():
            try:
                tutor_id = request.session.get('usuario_id')
                email_est = form.cleaned_data['email'] or f"est_{tutor_id}_{form.cleaned_data['nombres']}@neoteca.com"
                
                # 1. Llamar al SP para crear el Usuario Estudiante
                with connection.cursor() as cursor:
                    cursor.callproc('crear_usuario_seguro', [
                        email_est,
                        form.cleaned_data['password'],
                        form.cleaned_data['nombres'],
                        form.cleaned_data['apellidos'],
                        'ESTUDIANTE',
                        form.cleaned_data['carnet']
                    ])

                # 2. Vincularlo con el Tutor y Grado (Tabla Hija)
                # Recuperamos el usuario recién creado por el SP
                nuevo_usuario = Usuario.objects.get(email=email_est)
                tutor_obj = Tutor.objects.get(id_usuario=tutor_id)
                
                # Crear o actualizar registro en tabla ESTUDIANTE
                Estudiante.objects.update_or_create(
                    id_usuario=nuevo_usuario,
                    defaults={
                        'tutor': tutor_obj,
                        'grado': form.cleaned_data['grado']
                    }
                )

                messages.success(request, f"Estudiante {nuevo_usuario.nombres} inscrito correctamente.")
                return redirect('panel_tutor')

            except Exception as e:
                messages.error(request, f"Error de registro: {e}")
    else:
        form = RegistroEstudianteForm()

    return render(request, 'tutor_agregar_estudiante.html', {'form': form})