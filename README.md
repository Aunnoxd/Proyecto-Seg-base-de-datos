```markdown
# 📚 NEOTECA - Sistema de Biblioteca Escolar Segura

**Neoteca** es una plataforma integral para la gestión de bibliotecas escolares, diseñada bajo una **Arquitectura Híbrida** que combina la flexibilidad del desarrollo web moderno con la robustez de una base de datos empresarial.

Este proyecto destaca por delegar la lógica de negocio crítica (validaciones, auditoría y procesos masivos) directamente al motor de base de datos **Oracle**, garantizando la integridad y seguridad de la información.

---

## 🚀 Características Clave

### 🛡️ Seguridad Avanzada (Defensa en Profundidad)
* **Vinculación Familiar (Tokenización):** Sistema de login para menores mediante `TUT-TOKENS`, eliminando la necesidad de correos electrónicos.
* **Honeypot de Admin:** Panel falso en `/admin/` para detectar y bloquear intentos de intrusión.
* **Sesiones Inteligentes:** Cierre automático por inactividad (5 min) y políticas de *No-Cache* para evitar fugas de datos en equipos compartidos.
* **Data Masking & Cifrado:** Datos sensibles (direcciones, teléfonos) protegidos a nivel de base de datos.

### ⚡ Arquitectura Híbrida (Django + PL/SQL)
* **Procedimientos Almacenados:** Asignación de tareas a cursos enteros en milisegundos (`asignar_tarea_grado`).
* **Triggers de Auditoría:** Monitoreo en tiempo real de eliminaciones y accesos fuera de horario (`trg_audit_borrado`, `trg_no_leer_madrugada`).
* **Vistas Materializadas:** Generación de reportes de rendimiento y rankings sin impactar la velocidad del sitio web.

### 🎨 Experiencia de Usuario (UX)
* **Interfaz Profesional:** Diseño basado en *SB Admin 2* con feedback visual.
* **Panel de Tutor:** Visualización gráfica del progreso de lectura de los hijos.
* **Catálogo Visual:** Portadas de libros y sistema de lectura PDF con temporizador integrado.

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología | Uso |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 + Django 5.x | Lógica web y ORM |
| **Base de Datos** | Oracle Database 21c XE | Lógica de negocio (PL/SQL), Triggers, SPs |
| **Infraestructura** | Docker Desktop | Contenerización de la BD |
| **Conectividad** | python-oracledb | Driver nativo de conexión |
| **Frontend** | Bootstrap 4 + JS | Interfaz responsiva |

---

## 📂 Estructura del Proyecto

```text
neoteca_sistema/
├── neoteca/                # Aplicación Principal
│   ├── migrations/         # Historial de cambios en BD
│   ├── templates/          # Archivos HTML (Vistas)
│   ├── admin.py            # Configuración del Panel Admin
│   ├── models.py           # Modelos (Mapeo a Oracle)
│   └── views.py            # Controladores de lógica
├── neoteca_project/        # Configuración del Proyecto
│   ├── settings.py         # Configuración global
│   └── urls.py             # Rutas web
├── static/                 # CSS, JS, Imágenes del sistema
├── media/                  # Portadas y PDFs subidos
├── requirements.txt        # Dependencias del proyecto
├── manage.py               # Ejecutor de Django
└── .env                    # Variables de entorno (Se debe crear)
````

-----

## 🔧 Guía de Instalación

Sigue estos pasos para desplegar el proyecto en local.

### 1\. Configuración de Base de Datos

Asegúrate de tener Docker instalado y ejecuta el contenedor de Oracle:

```bash
docker run -d --name oracle-db \
  -p 1521:1521 \
  -e ORACLE_PWD=biblioteca_123 \
  gvenzl/oracle-xe
```

### 2\. Configuración del Entorno Python

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3\. Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto y agrega lo siguiente:

```ini
DEBUG=True
SECRET_KEY=tu_clave_secreta_segura
DB_USER=system
DB_PASSWORD=biblioteca_123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XE
```

### 4\. Ejecución

```bash
# Aplicar migraciones (Crear estructura en Oracle)
python manage.py migrate

# Iniciar el servidor
python manage.py runserver
```

Accede al sistema en: `http://127.0.0.1:8000`

-----

## 👤 Credenciales de Acceso (Demo)

| Rol | Usuario / Email | Contraseña | Funcionalidad |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@neoteca.com` | `admin123` | Gestión total + Auditoría |
| **Profesor** | `profe@neoteca.com` | `profe123` | Gestión de clases y libros |
| **Tutor** | `tutor@neoteca.com` | `tutor123` | Código vinculación: `TUT-DEMO` |
| **Estudiante** | *Nombre: Juan* | `juan123` | Requiere Código de Tutor |

-----

**Estado del Proyecto:** Finalizado (Defensa)  
**Desarrollado por:** [TUX]  
**Materia:** [Seguridad de Base de datos] - 2025

```