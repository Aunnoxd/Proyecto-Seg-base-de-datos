# /home/rubi/neoteca_sistema/neoteca/views_registry.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from .forms_registry import RegistroTutorForm, RegistroEstudianteForm
# IMPORTANTE: Importamos generar_codigo_tutor para usarlo manualmente
from .models import Tutor, Estudiante, Usuario, Grado, generar_codigo_tutor

# --- 1. REGISTRO PÚBLICO DE TUTOR ---
def registro_tutor(request):
    if request.method == 'POST':
        form = RegistroTutorForm(request.POST)
        if form.is_valid():
            try:
                # 1. Usamos el SP de Oracle para crear el Usuario Base
                with connection.cursor() as cursor:
                    cursor.callproc('crear_usuario_seguro', [
                        form.cleaned_data['email'],
                        form.cleaned_data['password'],
                        form.cleaned_data['nombres'],
                        form.cleaned_data['apellidos'],
                        'TUTOR', # Rol fijo
                        form.cleaned_data['carnet']
                    ])
                
                # 2. Recuperamos el usuario recién creado
                usuario_nuevo = Usuario.objects.get(email=form.cleaned_data['email'])
                
                # 3. Actualizamos datos extra en Django (Teléfono, Dirección)
                usuario_nuevo.telefono = form.cleaned_data['telefono']
                usuario_nuevo.direccion = form.cleaned_data['direccion']
                usuario_nuevo.save()
                
                # 4. CREACIÓN / ACTUALIZACIÓN DEL PERFIL TUTOR (Con Código Mágico)
                # get_or_create verifica si el SP ya creó la fila en la tabla TUTOR.
                tutor_obj, created = Tutor.objects.get_or_create(id_usuario=usuario_nuevo)

                # --- AQUÍ ESTÁ LA SOLUCIÓN ---
                # Si el tutor no tiene código (porque el SP lo creó vacío), se lo generamos ahora.
                if not tutor_obj.codigo_vinculacion:
                    tutor_obj.codigo_vinculacion = generar_codigo_tutor()
                    tutor_obj.save()

                # 5. Mensaje de éxito CON EL CÓDIGO VISIBLE
                codigo = tutor_obj.codigo_vinculacion
                messages.success(request, f"¡Cuenta creada! Su CÓDIGO DE VINCULACIÓN es: {codigo}. Guárdelo para inscribir a sus hijos.")
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
                # Generamos email ficticio si no tiene
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

                # 2. Vincularlo con el Tutor y Grado
                nuevo_usuario = Usuario.objects.get(email=email_est)
                tutor_obj = Tutor.objects.get(id_usuario=tutor_id)
                
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