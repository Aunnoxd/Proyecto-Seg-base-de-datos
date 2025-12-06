# /home/rubi/neoteca_sistema/neoteca/views.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import logout
from .models import Libro, Usuario
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login 
# --- VISTA DE LOGIN (CON ORACLE) ---
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        rol_detectado = None
        
        try:
            # 1. Validación contra ORACLE (Tu seguridad real)
            with connection.cursor() as cursor:
                rol_detectado = cursor.callfunc('verificar_login', str, [email, password])
        except Exception as e:
            messages.error(request, f"Error de conexión: {e}")
            return render(request, 'login.html')

        if rol_detectado:
            try:
                usuario = Usuario.objects.get(email=email)
                
                # Guardamos tu sesión personalizada
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_rol'] = rol_detectado
                request.session['usuario_nombre'] = usuario.nombres

                messages.success(request, f"Bienvenido, {usuario.nombres}")

                # --- REDIRECCIÓN Y PUENTE AL ADMIN ---
                if rol_detectado == 'ESTUDIANTE':
                    return redirect('lista_libros')
                elif rol_detectado == 'TUTOR':
                    return redirect('panel_tutor')
                elif rol_detectado == 'PROFESOR':
                    return redirect('mi_clase')
                
                elif rol_detectado == 'ADMIN':
                    # =====================================================
                    # EL TRUCO: Autologuear en Django Admin
                    # =====================================================
                    # Buscamos un superusuario de Django para "prestarle" la sesión
                    # Asegúrate de haber creado uno con 'python manage.py createsuperuser'
                    superuser_django = User.objects.filter(is_superuser=True).first()
                    
                    if superuser_django:
                        # Esto crea la sesión para /admin_django/ automáticamente
                        auth_login(request, superuser_django) 
                    
                    return redirect('gestion_libros') # Tu panel personalizado
                
                else:
                    return redirect('home')

            except Usuario.DoesNotExist:
                messages.error(request, "Error: Usuario en Oracle pero no en Django.")
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, 'login.html')

# --- VISTA DE LOGOUT ---
def logout_view(request):
    request.session.flush() # Borra toda la cookie de sesión
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect('login')

# --- VISTA PRINCIPAL (HOME) ---
def principal(request):
    # Verificamos si hay sesión activa para cambiar el menú en el HTML
    usuario_nombre = request.session.get('usuario_nombre')

    total_libros = Libro.objects.count()
    # Filtramos usando el campo 'rol' del modelo Usuario
    total_estudiantes = Usuario.objects.filter(rol='ESTUDIANTE').count()
    total_profesores = Usuario.objects.filter(rol='PROFESOR').count()
    
    contexto = {
        'total_libros': total_libros,
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
        'usuario_nombre': usuario_nombre
    }
    
    return render(request, 'index.html', contexto)