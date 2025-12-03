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
# Importamos el Dashboard (principal) del views.py general
from neoteca.views import principal 
from neoteca.admin_views import subir_libro
# Importamos las vistas del estudiante
from neoteca.estudiante_views import lista_libros, mis_asignaciones, registrar_lectura, registrar_tiempo_ajax, ver_libro_pdf# Importamos la vista del profesor (si ya la creaste)
from neoteca.profesor_views import mi_clase, asignar_tarea
from django.conf import settings 
from django.conf.urls.static import static 
from neoteca import views
from neoteca.tutor_views import panel_tutor
from neoteca.views_registry import registro_tutor, registrar_estudiante_por_tutor

urlpatterns = [
    # 1. TU RUTA PERSONALIZADA DEBE IR PRIMERO QUE EL ADMIN GENERAL
    path('admin/subir-libro/', subir_libro, name='subir_libro'), 
    
    # 2. RUTA GENERAL DEL ADMIN (DEBE IR DESPUÉS)
    path('admin/', admin.site.urls), 
    
    # 3. Resto de tus rutas
    path('', principal, name='home'),
    path('libros/', lista_libros, name='lista_libros'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mis-tareas/', mis_asignaciones, name='mis_asignaciones'),
    path('profesor/clase/', mi_clase, name='mi_clase'),
    path('profesor/asignar-tarea/', asignar_tarea, name='asignar_tarea'),
    path('libros/registrar/<int:libro_id>/', registrar_lectura, name='registrar_lectura'), 
    path('libros/leer/<int:id_libro>/', ver_libro_pdf, name='ver_libro_pdf'),
    path('api/guardar-tiempo/', registrar_tiempo_ajax, name='registrar_tiempo_ajax'),
    path('tutor/mi-panel/', panel_tutor, name='panel_tutor'),
    path('registro/tutor/', registro_tutor, name='registro_tutor'),
    path('tutor/inscribir-estudiante/', registrar_estudiante_por_tutor, name='registrar_estudiante'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)