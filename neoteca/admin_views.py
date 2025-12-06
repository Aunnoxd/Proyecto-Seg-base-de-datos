#admin_views.py
# /home/rubi/neoteca_sistema/neoteca/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Libro
from .forms_book import LibroForm # Asegúrate de tener este form creado

# --- DECORADOR DE PERMISOS ---
# Esto asegura que solo Admins y Profesores entren aquí.
# Si entra un Estudiante o Invitado, lo saca.
def solo_staff(view_func):
    def wrapper(request, *args, **kwargs):
        rol = request.session.get('usuario_rol')
        if rol not in ['ADMIN', 'PROFESOR']:
            messages.error(request, " Acceso restringido a personal autorizado.")
            return redirect('home') # O al login
        return view_func(request, *args, **kwargs)
    return wrapper

# ==========================================
# 1. VISTA PRINCIPAL: GESTIÓN DE LIBROS (LISTA)
# ==========================================
@solo_staff
def gestion_libros(request):
    # Traemos todos los libros ordenados del más nuevo al más viejo
    libros = Libro.objects.all().order_by('-id_libro')
    
    contexto = {
        'libros': libros
    }
    return render(request, 'admin_gestion_libros.html', contexto)

# ==========================================
# 2. VISTA: SUBIR LIBRO
# ==========================================
@solo_staff
def subir_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            # Guardamos quién lo subió (ID del usuario en sesión)
            libro.id_usuario_subio_id = request.session.get('usuario_id') 
            libro.save()
            
            messages.success(request, f"Libro '{libro.titulo}' agregado correctamente.")
            return redirect('gestion_libros')
        else:
            messages.error(request, "Por favor corrige los errores del formulario.")
    else:
        form = LibroForm()

    contexto = {
        'form': form,
        'titulo': 'Registrar Nuevo Libro',
        'boton': 'Guardar Libro'
    }
    return render(request, 'subir_libro.html', contexto)

# ==========================================
# 3. VISTA: EDITAR LIBRO
# ==========================================
@solo_staff
def editar_libro(request, id_libro):
    # Buscamos el libro o damos error 404 si no existe
    libro = get_object_or_404(Libro, pk=id_libro)

    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, f"Libro '{libro.titulo}' actualizado.")
            return redirect('gestion_libros')
        else:
            messages.error(request, "Error al actualizar.")
    else:
        form = LibroForm(instance=libro)

    contexto = {
        'form': form,
        'titulo': f'Editar: {libro.titulo}',
        'boton': 'Actualizar Cambios'
    }
    return render(request, 'subir_libro.html', contexto)

# ==========================================
# 4. VISTA: ELIMINAR LIBRO
# ==========================================
@solo_staff
def eliminar_libro(request, id_libro):
    libro = get_object_or_404(Libro, pk=id_libro)
    titulo = libro.titulo
    
    try:
        libro.delete()
        messages.success(request, f"🗑️ Se eliminó el libro '{titulo}'.")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")

    return redirect('gestion_libros')