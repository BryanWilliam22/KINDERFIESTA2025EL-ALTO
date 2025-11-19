KinderFiesta - El Alto - INNOVADEV

Plataforma web completa para la búsqueda, registro y calificación de salones infantiles en El Alto, Bolivia. 
Los usuarios pueden buscar locales, ver fotos, horarios, ubicación en mapa y dejar reseñas.
Los administradores pueden aprobar nuevos locales, moderar comentarios y garantizar que la plataforma sea segura y confiable.

REQUESITOS PREVIOS: 
- Visual Studio Code
- Python 3.11 o superior
- MySQL Workbench 8.0 o superior instalado y ejecutándose
- pip (gestor de paquetes de Python)
- Git

INSTALACIÓN:

1. Clona el repositorio:
   
git clone https://github.com/eateluisalbertomontoyase-glitch/KINDERFIESTA2025EL-ALTO.git
cd KINDERFIESTA2025EL-ALTO

2. Crea un entorno virtual (recomendado):
   
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate

3. Instala las dependencias:
   
pip install -r requirements.txt

4. Crea la base de datos en MySQL: MySQL Workbench Y ejecuta lo siguiente

CREATE DATABASE kinderfiesta CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE kinderfiesta;
(Aquí importa las tablas desde database_setup.sql)

5. Configura tus credenciales: Abre el archivo database.py y reemplaza los datos de conexión

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',               # Tu usuario MySQL
    'password': 'Tu contraseña',  # Tu contraseña MySQL
    'database': 'kinderfiesta',   # (Nombre del base de datos MYSQL)
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'

}

6. Ejecuta: Con el siguiente comando en la terminal

   python app.py

8. Abre en tu navegador:

Página principal (usuario): http://localhost:5000/
Panel de administración: http://localhost:5000/admin/login
-Usuario: admin@kinderfiesta.com
-Contraseña: admin123

| Cómo usar la plataforma |

Como usuario:

- Abre http://localhost:5000/
- Busca un salón por nombre o dirección
- Haz clic en un salón para ver más detalles
- Califica con estrellas y deja un comentario (máximo 500 caracteres)
- Para registrar tu salón, haz clic en "Registrar local" y completa el formulario (se requiere aprobación)

Como administrador:
- Ingresa a http://localhost:5000/admin/login
  Usa: admin@kinderfiesta.com
  Contraseña : admin123
En el panel puedes:
- Ver todas las solicitudes pendientes
- Aprobar o rechazar nuevos locales
- Ocultar o eliminar salones
- Editar o eliminar comentarios inapropiado

CARACTERISTICAS DE KINDERFIESTA: En primer lugra abunda dos visualizaciones uno
Para usuarios:

- Búsqueda de salones por nombre o dirección
- Visualización de fotos, horarios y contacto de cada local
- Ubicación en Google Maps
- Sistema de reseñas con calificación de 1 a 5 estrellas
- Comentarios (con filtrado automático de palabras ofensivas)
- Registro de nuevos salones (requiere aprobación del administrador)

Para administradores:

- Aprobar o rechazar solicitudes de nuevos locales
- Ocultar salones temporalmente
- Eliminar salones permanentemente
- Editar o eliminar comentarios inapropiados
- Visualizar estadísticas de calificaciones(En mejora)
- Panel seguro con login

Ya dentro de lo que es la seguridad y como tal la moderación seria:

- Filtrado automático de lenguaje ofensivo
- Control de acceso mediante sesiones(Mejora)
- Credenciales de base de datos protegidas (no se suben a GitHub)
- Validación de datos en cliente y servidor (Proceso)


  Si desea ontribuir con mejoras, bienvenido:

- Haz un Fork del repositorio
- Crea una rama nueva (git checkout -b feature/tu-mejora)
- Haz commit de tus cambios
- Sube tu rama y abre un Pull Request

AUTOR: INNOVADEV

## Instalación (Corrección y Mejora)


👉 Este cambio es perfecto porque mejora la claridad del proyecto sin modificar el código.

---

# ✅ OPCIÓN 2: Mejorar seguridad en database.py (comentarios útiles)

Puedes agregar comentarios explicativos (esto cuenta como mejora).

```python
# Se agregó explicación sobre la importancia de no subir credenciales reales a GitHub
# También se recomienda usar variables de entorno para mayor seguridad.

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',                     # Se recomienda crear un usuario con menos privilegios
    'password': 'TU_CONTRASEÑA',        # No subir la contraseña real al repositorio
    'database': 'kinderfiesta',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}
