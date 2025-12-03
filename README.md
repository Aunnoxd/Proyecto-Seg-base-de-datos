
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
````

### 2\. Configurar Entorno Virtual

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# venv\Scripts\activate   # En Windows
pip install -r requirements.txt
```

### 3\. Configurar Base de Datos (Docker)

Asegúrate de tener el contenedor de Oracle corriendo:

```bash
docker run -d -p 1521:1521 -e ORACLE_PWD=biblioteca_123 --name oracle_db gvenzl/oracle-xe
```

*Nota: Debes ejecutar los scripts SQL ubicados en la carpeta `/sql_scripts` para crear las tablas, triggers y procedimientos.*

### 4\. Ejecutar el Servidor

```bash
python manage.py runserver
```

## 📸 Capturas de Pantalla

*(Aquí puedes agregar imágenes de tu sistema funcionando)*

-----

Desarrollado para la asignatura de Seguridad de Bases de Datos.

````

### PASO 4: Subir a GitHub (Comandos)

Ahora sí, ve a tu terminal (en la carpeta del proyecto) y ejecuta estos comandos uno por uno:

1.  **Inicializar Git:**
    ```bash
    git init
    ```

2.  **Agregar todos los archivos (respetando el .gitignore):**
    ```bash
    git add .
    ```

3.  **Hacer el primer "paquete" (Commit):**
    ```bash
    git commit -m "Versión 1.0: Sistema completo con Roles, Oracle Triggers y Timer PDF"
    ```

4.  **Cambiar a la rama principal:**
    ```bash
    git branch -M main
    ```

5.  **Conectar con tu repositorio:**
    ```bash
    git remote add origin https://github.com/Aunnoxd/Proyecto-Seg-base-de-datos.git
    ```

6.  **Subir los archivos:**
    ```bash
    git push -u origin main
    ```

¡Y listo! Tu proyecto estará en línea con una presentación profesional. Avísame cuando termine de subir para continuar con el **Registro de Usuarios**.
````
