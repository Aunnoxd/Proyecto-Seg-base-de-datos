# /home/rubi/neoteca_sistema/neoteca/views.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import logout
# Importamos los modelos necesarios
from .models import Libro, Usuario, Estudiante, Tutor
# Importamos lo necesario para el login automático de Django Admin
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login 

# --- VISTA DE LOGIN (CON DOBLE LÓGICA) ---
def login_view(request):
    if request.method == 'POST':
        tipo_login = request.POST.get('tipo_login') # Recibimos 'general' o 'estudiante' del HTML

        # =======================================================
        # OPCIÓN A: LOGIN GENERAL (Email + Password)
        # Para Admin, Tutor y Profesor
        # =======================================================
        if tipo_login == 'general':
            email = request.POST.get('email')
            password = request.POST.get('password')
            rol_detectado = None
            
            try:
                # 1. Validación contra ORACLE
                with connection.cursor() as cursor:
                    rol_detectado = cursor.callfunc('verificar_login', str, [email, password])
            except Exception as e:
                messages.error(request, f"Error de conexión: {e}")
                return render(request, 'login.html')

            if rol_detectado:
                try:
                    usuario = Usuario.objects.get(email=email)
                    
                    # Guardamos sesión personalizada
                    crear_sesion_personalizada(request, usuario, rol_detectado)

                    # --- LÓGICA ESPECIAL PARA ADMIN (TU PUENTE MÁGICO) ---
                    if rol_detectado == 'ADMIN':
                        # Buscamos un superusuario de Django para "prestarle" la sesión
                        superuser_django = User.objects.filter(is_superuser=True).first()
                        
                        if superuser_django:
                            auth_login(request, superuser_django) # Login silencioso en Django Admin
                        
                        return redirect('gestion_libros') # Tu panel personalizado
                    
                    # --- REDIRECCIONES NORMALES ---
                    elif rol_detectado == 'TUTOR':
                        return redirect('panel_tutor')
                    elif rol_detectado == 'PROFESOR':
                        return redirect('mi_clase')
                    elif rol_detectado == 'ESTUDIANTE': # Por si un estudiante entra con email
                        return redirect('lista_libros')
                    else:
                        return redirect('home')

                except Usuario.DoesNotExist:
                    messages.error(request, "Error: Usuario en Oracle pero no en Django.")
            else:
                messages.error(request, "Credenciales incorrectas.")
# =======================================================
        # OPCIÓN B: LOGIN ESTUDIANTE (Nombre + Código Tutor)
        # =======================================================
        elif tipo_login == 'estudiante':
            nombre_estudiante = request.POST.get('nombre')
            codigo_tutor = request.POST.get('codigo_tutor')
            password_est = request.POST.get('password')

            try:
                # 1. Buscar al Tutor por su código único
                tutor_padre = Tutor.objects.get(codigo_vinculacion=codigo_tutor)
                
                # 2. Buscar al Estudiante (SOLO POR NOMBRE Y TUTOR)
                # Quitamos la contraseña del filtro porque está encriptada
                estudiante = Estudiante.objects.select_related('id_usuario').filter(
                    tutor=tutor_padre,
                    id_usuario__nombres__icontains=nombre_estudiante 
                ).first()

                if estudiante:
                    # 3. VERIFICACIÓN SEGURA CON ORACLE
                    # Recuperamos el email interno del estudiante para validar su password
                    email_interno = estudiante.id_usuario.email
                    
                    rol_detectado = None
                    try:
                        with connection.cursor() as cursor:
                            # Usamos la misma función de seguridad que el login normal
                            rol_detectado = cursor.callfunc('verificar_login', str, [email_interno, password_est])
                    except Exception:
                        pass # Si falla Oracle, rol_detectado seguirá siendo None

                    if rol_detectado == 'ESTUDIANTE':
                        # ¡Contraseña Correcta!
                        crear_sesion_personalizada(request, estudiante.id_usuario, 'ESTUDIANTE')
                        return redirect('lista_libros')
                    else:
                        messages.error(request, "Contraseña incorrecta.")
                else:
                    messages.error(request, "No se encontró un estudiante con ese nombre vinculado a este Tutor.")

            except Tutor.DoesNotExist:
                messages.error(request, "El código de Tutor no existe.")
            except Exception as e:
                messages.error(request, f"Error del sistema: {e}")

    return render(request, 'login.html')

# --- FUNCIÓN AUXILIAR PARA NO REPETIR CÓDIGO ---
def crear_sesion_personalizada(request, usuario, rol):
    request.session['usuario_id'] = usuario.id_usuario
    request.session['usuario_rol'] = rol
    request.session['usuario_nombre'] = usuario.nombres
    messages.success(request, f"Bienvenido, {usuario.nombres}")

# --- VISTA DE LOGOUT ---
def logout_view(request):
    request.session.flush() 
    logout(request) # Cierra también la sesión de Django Admin si existía
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login')

# --- VISTA PRINCIPAL (HOME) ---
def principal(request):
    usuario_nombre = request.session.get('usuario_nombre')
    total_libros = Libro.objects.count()
    total_estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').count()
    total_profesores = Usuario.objects.filter(rol='PROFESOR').count()
    
    contexto = {
        'total_libros': total_libros,
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
        'usuario_nombre': usuario_nombre
    }
    return render(request, 'index.html', contexto)

#Alerta de seguridad de link
def alerta_seguridad(request):
    # Opcional: Podrías registrar aquí en tu BD que alguien intentó entrar
    contexto = {
        'ip_usuario': request.META.get('REMOTE_ADDR')
    }
    return render(request, 'security_alert.html', contexto)