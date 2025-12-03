# /home/rubi/neoteca_sistema/neoteca/views.py

from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.contrib.auth import logout
from .models import Libro, Usuario

# --- VISTA DE LOGIN (CON ORACLE) ---
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        rol_detectado = None
        
        try:
            # 1. Llamada a la Función Almacenada en Oracle
            with connection.cursor() as cursor:
                # Se asume que la función SQL retorna el nombre del ROL (VARCHAR) o NULL
                rol_detectado = cursor.callfunc('verificar_login', str, [email, password])
        except Exception as e:
            messages.error(request, f"Error de conexión con Oracle: {e}")
            return render(request, 'login.html')

        if rol_detectado:
            # 2. Recuperar el objeto Usuario de Django para obtener el ID
            try:
                usuario = Usuario.objects.get(email=email)
                
                # 3. GUARDAR EN SESIÓN (Lo más importante)
                request.session['usuario_id'] = usuario.id_usuario
                request.session['usuario_rol'] = rol_detectado
                request.session['usuario_nombre'] = usuario.nombres

                messages.success(request, f"Bienvenido, {usuario.nombres} ({rol_detectado})")

                # 4. Redirección según ROL
                if rol_detectado == 'ESTUDIANTE':
                    return redirect('lista_libros') # O 'estudiante_dashboard' si tienes uno
                elif rol_detectado == 'PROFESOR':
                    # return redirect('profesor_dashboard') # A futuro
                    return redirect('home')
                elif rol_detectado == 'ADMIN':
                    return redirect('/admin/')
                else:
                    return redirect('home')

            except Usuario.DoesNotExist:
                messages.error(request, "Error de integridad: El usuario existe en SQL pero no en Django ORM.")
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