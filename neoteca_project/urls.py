"""
URL configuration for neoteca_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# /home/rubi/neoteca_sistema/neoteca_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static 

# --- IMPORTACIONES ---
from neoteca.views import principal, login_view, logout_view, alerta_seguridad
from neoteca.estudiante_views import (
    lista_libros, mis_asignaciones, registrar_lectura, 
    registrar_tiempo_ajax, ver_libro_pdf
)
from neoteca.profesor_views import mi_clase, asignar_tarea, asignar_masivo, eliminar_tarea
from neoteca.tutor_views import panel_tutor
from neoteca.views_registry import registro_tutor, registrar_estudiante_por_tutor

# Importamos TODAS las vistas del Admin (CRUD)
from neoteca.admin_views import (
    gestion_libros, subir_libro, editar_libro, eliminar_libro
)

urlpatterns = [
    # ==========================================
    # 0. TRAMPA DE SEGURIDAD (HONEYPOT)
    # ==========================================
    path('admin/', alerta_seguridad, name='alerta_seguridad'),
    # ==========================================
    # 1. ADMINISTRACIÓN NEOTECA (CRUD LIBROS)
    # ==========================================
    # ¡ESTA ES LA LÍNEA QUE FALTABA Y CAUSABA EL ERROR!
    path('admin/gestion-libros/', gestion_libros, name='gestion_libros'),
    
    path('admin/subir-libro/', subir_libro, name='subir_libro'),
    path('admin/editar-libro/<int:id_libro>/', editar_libro, name='editar_libro'),
    path('admin/eliminar-libro/<int:id_libro>/', eliminar_libro, name='eliminar_libro'),

    # ==========================================
    # 2. ADMIN GENERAL DE DJANGO
    # ==========================================
    path('admin_django/', admin.site.urls), # Cambié a admin_django para no chocar nombres

    # ==========================================
    # 3. VISTAS GENERALES (LOGIN/HOME)
    # ==========================================
    path('', principal, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # ==========================================
    # 4. VISTAS DE ESTUDIANTE
    # ==========================================
    path('libros/', lista_libros, name='lista_libros'),
    path('mis-tareas/', mis_asignaciones, name='mis_asignaciones'),
    path('libros/registrar/<int:libro_id>/', registrar_lectura, name='registrar_lectura'), 
    path('libros/leer/<int:id_libro>/', ver_libro_pdf, name='ver_libro_pdf'),
    path('api/guardar-tiempo/', registrar_tiempo_ajax, name='registrar_tiempo_ajax'),

    # ==========================================
    # 5. VISTAS DE PROFESOR
    # ==========================================
    path('profesor/clase/', mi_clase, name='mi_clase'),
    path('profesor/asignar-tarea/', asignar_tarea, name='asignar_tarea'),
    path('profesor/asignar-masivo/', asignar_masivo, name='asignar_masivo'),
    path('profesor/eliminar-tarea/<int:id_asignacion>/', eliminar_tarea, name='eliminar_tarea'),
    
    # ==========================================
    # 6. VISTAS DE TUTOR Y REGISTRO
    # ==========================================
    path('tutor/mi-panel/', panel_tutor, name='panel_tutor'),
    path('registro/tutor/', registro_tutor, name='registro_tutor'),
    path('tutor/inscribir-estudiante/', registrar_estudiante_por_tutor, name='registrar_estudiante'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)