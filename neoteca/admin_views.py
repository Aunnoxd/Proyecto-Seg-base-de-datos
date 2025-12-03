# /home/rubi/neoteca_sistema/neoteca/admin_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms_book import LibroForm
from .models import Libro

# --- CHECK DE PERMISOS: Admin o Profesor ---
def tiene_permiso_gestion(request):
    rol = request.session.get('usuario_rol')
    return rol in ['ADMIN', 'PROFESOR']

# --- DECORADOR ---
def solo_staff(view_func):
    def wrapper(request, *args, **kwargs):
        if not tiene_permiso_gestion(request):
            messages.error(request, "Acceso Denegado. Solo Admin y Profesores.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

# --- 1. READ: Listar Libros ---
@solo_staff
def gestion_libros(request):
    libros = Libro.objects.all().order_by('-id_libro')
    return render(request, 'admin_gestion_libros.html', {'libros': libros})

# --- 2. CREATE: Subir Libro ---
@solo_staff
def subir_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES) 
        if form.is_valid():
            libro = form.save()
            messages.success(request, f" Libro '{libro.titulo}' agregado correctamente.")
            return redirect('gestion_libros')
        else:
            messages.error(request, " Error en el formulario.")
    else:
        form = LibroForm()
    
    contexto = {
        'form': form,
        'titulo': 'Registrar Nuevo Libro',
        'boton': 'Guardar Libro'
    }
    return render(request, 'subir_libro.html', contexto)

# --- 3. UPDATE: Editar Libro ---
@solo_staff
def editar_libro(request, id_libro):
    libro = get_object_or_404(Libro, pk=id_libro)
    
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES, instance=libro)
        if form.is_valid():
            form.save()
            messages.success(request, f" '{libro.titulo}' actualizado.")
            return redirect('gestion_libros')
    else:
        form = LibroForm(instance=libro)
        
    contexto = {
        'form': form,
        'titulo': f'Editar: {libro.titulo}',
        'boton': 'Actualizar Cambios'
    }
    return render(request, 'subir_libro.html', contexto)

# --- 4. DELETE: Eliminar Libro ---
@solo_staff
def eliminar_libro(request, id_libro):
    # OPCIONAL: Si quieres que SOLO EL ADMIN pueda borrar (y el profe no),
    # descomenta las siguientes lineas:
    # if request.session.get('usuario_rol') != 'ADMIN':
    #     messages.error(request, "Solo el Administrador puede eliminar libros.")
    #     return redirect('gestion_libros')

    libro = get_object_or_404(Libro, pk=id_libro)
    titulo_temp = libro.titulo
    try:
        libro.delete() 
        messages.success(request, f"Se eliminó '{titulo_temp}'.")
    except Exception as e:
        messages.error(request, f"Error DB: {e}")
        
    return redirect('gestion_libros')