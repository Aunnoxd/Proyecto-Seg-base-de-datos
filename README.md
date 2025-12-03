# 📚 Neoteca - Sistema de Biblioteca Escolar Seguro

Sistema de gestión bibliotecaria desarrollado con **Django 5** y **Oracle Database 21c**, enfocado en la seguridad de datos, auditoría y roles jerárquicos.

## 🚀 Características Principales

### 🔐 Seguridad y Base de Datos (Oracle 21c)
* **Arquitectura "Table-per-Type":** Implementación de herencia en SQL (Usuario -> Estudiante/Profesor/Tutor).
* **Seguridad en Capa de Datos:** El Login y las validaciones críticas se realizan mediante **Stored Procedures** y **Funciones PL/SQL**, no solo en Django.
* **Auditoría Automática:** Triggers en Oracle que registran cualquier eliminación o cambio sensible en una tabla de auditoría inmutable.
* **Encriptación:** Datos sensibles protegidos a nivel de base de datos.

### 👥 Módulos por Roles
1.  **Estudiante:**
    * Catálogo filtrado por Grado Escolar.
    * Visor de PDF con **Timer de Lectura** (validación de tiempo real).
    * Sistema de tareas y progreso.
2.  **Profesor:**
    * Gestión de Clase y asignación de tareas.
    * Monitoreo visual del progreso de sus alumnos.
3.  **Tutor (Familia):**
    * Panel exclusivo para monitorear el avance de sus hijos/pupilos.
4.  **Administrador:**
    * CRUD de Libros con interfaz moderna (DataTables).
    * Gestión de usuarios y reportes de seguridad.

## 🛠️ Tecnologías

* **Backend:** Python 3.13, Django 5.2.
* **Base de Datos:** Oracle Database 21c Express Edition (Docker).
* **Frontend:** Bootstrap 4, SB Admin 2, JavaScript (AJAX).
* **Librerías Clave:** `cx_Oracle`, `django-jazzmin`.

## 📦 Instalación y Despliegue

### 1. Clonar el repositorio
```bash
git clone [https://github.com/Aunnoxd/Proyecto-Seg-base-de-datos.git](https://github.com/Aunnoxd/Proyecto-Seg-base-de-datos.git)
cd Proyecto-Seg-base-de-datos
