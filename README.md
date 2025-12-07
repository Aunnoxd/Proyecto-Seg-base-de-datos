# 📚 NEOTECA - Sistema de Biblioteca Escolar Segura

**Neoteca** es una plataforma integral para la gestión de bibliotecas escolares, diseñada con una **Arquitectura Híbrida** que combina la flexibilidad de **Django (Python)** con la potencia y seguridad de **Oracle Database (PL/SQL)**.

El sistema prioriza la **seguridad del menor**, implementando login sin correo electrónico para estudiantes, monitoreo parental y protección de datos sensibles directamente en la base de datos.

---

## 🚀 Características Principales

### 🛡️ Seguridad y Auditoría (Defensa en Profundidad)
* **Honeypot:** Panel de administración falso (`/admin/`) para detectar intrusos.
* **Sesiones Seguras:** Cierre automático por inactividad (5 min) y limpieza de caché (No-Cache Headers) al salir.
* **Data Masking:** Encriptación de datos sensibles en Oracle.
* **Auditoría Activa:** Triggers que registran cambios críticos en `LOG_AUDITORIA`.

### 👨‍👩‍👧‍👦 Vinculación Familiar (Tokenización)
* **Tokens de Vinculación:** Los tutores generan un código único (ej: `TUT-4829`).
* **Login de Estudiante:** Los niños acceden usando su **Nombre + Código del Padre**, eliminando la necesidad de correos electrónicos para menores.

### ⚡ Lógica Híbrida (Django + Oracle PL/SQL)
* **Asignación Masiva:** Procedimientos Almacenados que asignan tareas a grados completos en milisegundos.
* **Control de Lectura:** Triggers que validan horarios (ej: prohibido leer de madrugada).
* **Reportes SQL:** Vistas materializadas para calcular el rendimiento y ranking de lectores sin sobrecargar el servidor web.

---

## 🛠️ Tecnologías Utilizadas

* **Backend:** Python 3.13, Django 5.x
* **Base de Datos:** Oracle Database 21c XE (Docker)
* **Driver:** python-oracledb
* **Frontend:** HTML5, CSS3, Bootstrap 4 (Plantilla SB Admin 2)
* **Herramientas:** VS Code, Docker Desktop

---

## 🔧 Instalación y Configuración

### 1. Prerrequisitos
* Tener **Docker** instalado y corriendo con Oracle XE.
* Tener **Python** instalado.

### 2. Configuración de Base de Datos
Ejecutar el contenedor de Oracle:
```bash
docker run -d --name oracle-db -p 1521:1521 -e ORACLE_PWD=biblioteca_123 gvenzl/oracle-xe

# Clonar el repositorio (si aplica) o descargar carpeta
cd neoteca_sistema

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install django python-oracledb Pillow python-dotenv jazzmin

# Ejecutar migraciones (Estructura Django)
python manage.py migrate

# Iniciar servidor
python manage.py runserver

### 2. ¿Cómo ver cuánto pesa tu proyecto?

Si estás en Linux (WSL) o Mac, usa la terminal. Es la forma más precisa.

**Paso A: Ver el peso total**
Estando en la carpeta de tu proyecto (`neoteca_sistema`), escribe:

```bash
du -sh .