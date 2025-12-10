#  NEOTECA - Sistema de Biblioteca Escolar Segura

**Neoteca** es una plataforma integral para la gestión de bibliotecas escolares virtuales, diseñada bajo una **Arquitectura Híbrida** que combina la flexibilidad del desarrollo web moderno con la robustez de una base de datos empresarial.

Este proyecto destaca por delegar la lógica de negocio crítica (validaciones, auditoría y procesos masivos) directamente al motor de base de datos **Oracle**, garantizando la integridad y seguridad de la información.

 Guía de Instalación y Despliegue
PASO 1: Base de Datos (Elige UNA opción)
🔵 OPCIÓN A: Docker (Recomendada para Linux/Mac)

Si tienes Docker instalado, es la forma más rápida de tener el entorno limpio.
Bash

# 1. Iniciar el contenedor
docker run -d --name oracle-db \
  -p 1521:1521 \
  -e ORACLE_PWD=biblioteca_123 \
  gvenzl/oracle-xe

# 2. Copiar el respaldo DMP al contenedor
docker cp neoteca_full.dmp oracle-db:/opt/oracle/admin/XE/dpdump/

# 3. Dar permisos y restaurar
docker exec -u 0 oracle-db chmod 777 /opt/oracle/admin/XE/dpdump/neoteca_full.dmp
docker exec oracle-db impdp system/biblioteca_123 directory=DATA_PUMP_DIR dumpfile=neoteca_full.dmp table_exists_action=REPLACE

🟠 OPCIÓN B: Windows Nativo (Fácil para el Equipo)

Si no usas Docker, instala Oracle Database 21c XE para Windows y sigue estos pasos:

    Abre una terminal (CMD o PowerShell) en la carpeta del proyecto.

    Ejecuta el script SQL universal que crea tablas, procedimientos y datos:

Bash

sqlplus system/biblioteca_123 @neoteca_full_script.sql

(Si no tienes sqlplus en el PATH, puedes abrir el archivo .sql en SQL Developer y ejecutarlo todo).
PASO 2: Configuración del Entorno Python
Bash

# Crear entorno virtual
python -m venv venv

# Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

PASO 3: Variables de Entorno

Crea un archivo llamado .env en la raíz del proyecto y agrega lo siguiente:
Ini, TOML

DEBUG=True
SECRET_KEY=tu_clave_secreta_neoteca_2025
DB_USER=system
DB_PASSWORD=biblioteca_123
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=XE

PASO 4: Ejecución
Bash

# Iniciar el servidor web
python manage.py runserver

Accede al sistema en: http://127.0.0.1:8000
👤 Credenciales de Acceso (Demo)
Rol	Usuario / Email	Contraseña	Funcionalidad
Administrador	admin@neoteca.com	admin1 Gestión total + Auditoría Técnica
Profesor	profe@neoteca.com	profe1	Asignación masiva y gestión de lectura
Tutor	leotutor@neoteca.com leo1	Código vinculación: TUT-9091
Estudiante	Nombre: Mafalda	mafalda1	TUT-9091 Requiere Código de Tutor

Estado del Proyecto: Finalizado (Defensa)

Desarrollado por: [TUX]

Materia: Seguridad de Base de Datos - 2025
