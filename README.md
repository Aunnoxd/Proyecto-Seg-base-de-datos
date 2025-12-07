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
├── neoteca_full.dmp        # RESPALDO COMPLETO DE ORACLE (Importar)
├── requirements.txt        # Dependencias del proyecto
├── manage.py               # Ejecutor de Django
└── .env                    # Variables de entorno

🔧 Guía de Instalación y Despliegue
1. Despliegue de Base de Datos (Docker)

Este paso es crucial para levantar Oracle 21c XE.
Bash

# 1. Iniciar el contenedor
docker run -d --name oracle-db \
  -p 1521:1521 \
  -e ORACLE_PWD=biblioteca_123 \
  gvenzl/oracle-xe

2. Restauración de Datos y Lógica (IMPORTANTE)

El sistema utiliza Procedimientos Almacenados y Triggers que deben importarse.
Bash

# 1. Copiar el archivo de respaldo al contenedor
docker cp neoteca_full.dmp oracle-db:/opt/oracle/admin/XE/dpdump/

# 2. Dar permisos de lectura al archivo (Fix de permisos)
docker exec -u 0 oracle-db chmod 777 /opt/oracle/admin/XE/dpdump/neoteca_full.dmp

# 3. Ejecutar la importación (Data Pump)
docker exec oracle-db impdp system/biblioteca_123 directory=DATA_PUMP_DIR dumpfile=neoteca_full.dmp table_exists_action=REPLACE

Si la importación es exitosa, verá mensajes como "Processing object type SCHEMA_EXPORT/PROCEDURE".
3. Configuración del Entorno Python
Bash

# Crear entorno virtual
python -m venv venv

# Activar entorno (Windows)
venv\Scripts\activate
# Activar entorno (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

4. Variables de Entorno

Crea un archivo llamado .env en la raíz del proyecto y agrega lo siguiente:
Ini, TOML

DEBUG=True
SECRET_KEY=tu_clave_secreta_neoteca_2025
DB_USER=system
DB_PASSWORD=biblioteca_123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XE

5. Ejecución del Servidor
Bash

# Iniciar el servidor web
python manage.py runserver

Accede al sistema en: http://127.0.0.1:8000