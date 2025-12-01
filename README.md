# Proyecto Biblioteca Virtual (Seguridad de Base de Datos)

Este proyecto es un sistema de gestión bibliotecaria desarrollado en Django, utilizando **Oracle Database** como motor de base de datos.

## 🚀 Instalación para Colaboradores

Sigue estos pasos estrictamente para configurar el entorno local.

### 1. Clonar el repositorio
```bash
git clone [https://github.com/Aunnoxd/Proyecto-Seg-base-de-datos.git](https://github.com/Aunnoxd/Proyecto-Seg-base-de-datos.git)
cd Proyecto-Seg-base-de-datos


# Crear entorno
python -m venv venv

# Activar (Windows)
venv\Scripts\activate
# Activar (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt



🛠 Configuración de la Base de Datos (Oracle)

Este proyecto requiere Oracle Database XE. La forma recomendada (y la única soportada en este proyecto para Linux/Kali) es usando Docker.

Paso A: Instalar y Ejecutar Oracle en Docker

Ejecuta el siguiente comando para descargar y levantar la base de datos en el puerto 1521.

    Nota: Si estás en Linux y falla la descarga por DNS, revisa tu /etc/docker/daemon.json.

Bash

docker run -d --name oracle-db \
  -p 1521:1521 -p 5500:5500 \
  -e ORACLE_PASSWORD=biblioteca_123 \
  -e ORACLE_CHARACTERSET=AL32UTF8 \
  gvenzl/oracle-xe

Espera unos 2 minutos hasta que la base de datos arranque. Puedes verificarlo con: docker logs -f oracle-db (Hasta ver "DATABASE IS READY TO USE").

Paso B: Crear el Usuario y Permisos

Una vez lista la base de datos, debemos crear el usuario biblioteca.

    Entra a la consola SQL del contenedor:
    Bash

docker exec -it oracle-db sqlplus system/biblioteca_123

Copia y pega estos comandos SQL:
SQL

    CREATE USER biblioteca IDENTIFIED BY biblioteca_123;
    GRANT CONNECT, RESOURCE, DBA TO biblioteca;
    ALTER USER biblioteca QUOTA UNLIMITED ON USERS;
    EXIT;

Paso C: Migraciones de Django

Ahora que la base de datos existe, crea las tablas del sistema:
Bash

python manage.py migrate

Paso D: Crear Superusuario (Admin)

Para entrar al panel de administración:
Bash

python manage.py createsuperuser

▶️ Ejecutar el Proyecto

Bash

python manage.py runserver

Visita: http://127.0.0.1:8000

📂 Credenciales por defecto (Desarrollo)

    DB User: biblioteca

    DB Password: biblioteca_123

    DB Port: 1521
