# /home/rubi/neoteca_sistema/neoteca/views.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import logout
# Importamos los modelos necesarios
from .models import Libro, Usuario, Estudiante, Tutor
# Importamos lo necesario para el login automático de Django Admin
from django.contrib.auth.models import User
# --- IMPORTANTE: Traemos la función para verificar usuarios de Django ---
from django.contrib.auth import login as auth_login, authenticate 

# --- VISTA DE LOGIN (CON DOBLE LÓGICA) ---
def login_view(request):
    if request.method == 'POST':
        tipo_login = request.POST.get('tipo_login') 

        # =======================================================
        # OPCIÓN A: LOGIN GENERAL (Email/Usuario + Password)
        # =======================================================
        if tipo_login == 'general':
            email_input = request.POST.get('email') # Puede ser email o el usuario (ej: director_ana)
            password = request.POST.get('password')
            rol_detectado = None
            
            # 1. PRIMERO BUSCAMOS EN ORACLE (Profesores/Tutores)
            try:
                with connection.cursor() as cursor:
                    rol_detectado = cursor.callfunc('verificar_login', str, [email_input, password])
            except Exception as e:
                print(f"Aviso: {e}") # Si falla Oracle, seguimos intentando en Django

            if rol_detectado:
                # --- LÓGICA ORACLE (La que ya tenías) ---
                try:
                    usuario = Usuario.objects.get(email=email_input)
                    crear_sesion_personalizada(request, usuario, rol_detectado)

                    if rol_detectado == 'ADMIN':
                        # Puente Mágico al Admin de Django
                        superuser_django = User.objects.filter(is_superuser=True).first()
                        if superuser_django:
                            auth_login(request, superuser_django)
                        return redirect('gestion_libros')
                    elif rol_detectado == 'TUTOR':
                        return redirect('panel_tutor')
                    elif rol_detectado == 'PROFESOR':
                        return redirect('mi_clase')
                    elif rol_detectado == 'ESTUDIANTE':
                        return redirect('lista_libros')
                    else:
                        return redirect('home')

                except Usuario.DoesNotExist:
                    messages.error(request, "Error: Usuario en Oracle pero no en Django.")
            
            else:
                # --- 2. BUSCAMOS EN DJANGO (Directores/Auditores) ---
                # Si Oracle no lo conoce, preguntamos a la base de datos interna de Django
                user_django = authenticate(request, username=email_input, password=password)
                
                if user_django is not None:
                    # ¡Lo encontramos! Verificamos que tenga permiso de entrar
                    if user_django.is_active and user_django.is_staff:
                        auth_login(request, user_django)
                        # Lo mandamos directo al panel de administración gris
                        return redirect('/admin_django/')
                    else:
                        messages.error(request, "Usuario correcto pero no tiene permisos de Staff.")
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
                tutor_padre = Tutor.objects.get(codigo_vinculacion=codigo_tutor)
                estudiante = Estudiante.objects.select_related('id_usuario').filter(
                    tutor=tutor_padre,
                    id_usuario__nombres__icontains=nombre_estudiante 
                ).first()

                if estudiante:
                    # Validamos contraseña con Oracle
                    email_interno = estudiante.id_usuario.email
                    rol_detectado = None
                    try:
                        with connection.cursor() as cursor:
                            rol_detectado = cursor.callfunc('verificar_login', str, [email_interno, password_est])
                    except Exception: pass

                    if rol_detectado == 'ESTUDIANTE':
                        crear_sesion_personalizada(request, estudiante.id_usuario, 'ESTUDIANTE')
                        return redirect('lista_libros')
                    else:
                        messages.error(request, "Contraseña incorrecta.")
                else:
                    messages.error(request, "No se encontró estudiante con ese nombre y tutor.")

            except Tutor.DoesNotExist:
                messages.error(request, "El código de Tutor no existe.")
            except Exception as e:
                messages.error(request, f"Error del sistema: {e}")

    return render(request, 'login.html')

# --- FUNCIONES AUXILIARES ---
def crear_sesion_personalizada(request, usuario, rol):
    request.session['usuario_id'] = usuario.id_usuario
    request.session['usuario_rol'] = rol
    request.session['usuario_nombre'] = usuario.nombres
    messages.success(request, f"Bienvenido, {usuario.nombres}")

def logout_view(request):
    es_timeout = request.GET.get('timeout') == 'true'
    try:
        if 'usuario_id' in request.session: del request.session['usuario_id']
        if 'usuario_rol' in request.session: del request.session['usuario_rol']
    except KeyError: pass

    request.session.flush()
    logout(request) 
    
    if es_timeout:
        messages.warning(request, "Tu sesión se cerró por inactividad (Seguridad).")
    else:
        messages.info(request, "Sesión cerrada correctamente.")
        
    return redirect('login')

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

def alerta_seguridad(request):
    contexto = {'ip_usuario': request.META.get('REMOTE_ADDR')}
    return render(request, 'security_alert.html', contexto)