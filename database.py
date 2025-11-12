"""
KINDERFIESTA - Módulo de conexión a MySQL
Gestiona todas las operaciones con la base de datos
"""


import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
from datetime import timedelta



# ============================================
# CONFIGURACIÓN DE LA BASE DE DATOS
# ============================================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Tu contraseña
    'database': 'kinderfiesta',
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}



# ============================================
# GESTOR DE CONTEXTO PARA CONEXIONES
# ============================================
@contextmanager
def get_db_connection():
    """Crea una conexión a la base de datos y la cierra automáticamente"""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        yield connection
    except Error as e:
        print(f"Error de conexión a MySQL: {e}")
        raise
    finally:
        if connection and connection.is_connected():
            connection.close()



@contextmanager
def get_db_cursor(commit=False):
    """Obtiene un cursor para ejecutar consultas"""
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        try:
            yield cursor
            if commit:
                connection.commit()
        except Error as e:
            connection.rollback()
            print(f"Error en la consulta: {e}")
            raise
        finally:
            cursor.close()



# ============================================
# FUNCIONES PARA SALONES
# ============================================



def obtener_todos_salones():
    """Obtiene todos los salones con su información completa (solo visibles)"""
    try:
        with get_db_cursor() as cursor:
            # 🆕 Solo obtener salones visibles
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.phone,
                    s.address,
                    s.locationCode,
                    s.category,
                    s.rating,
                    s.visible,
                    COUNT(DISTINCT r.id) as num_reviews
                FROM salones s
                LEFT JOIN reviews r ON s.id = r.salon_id
                WHERE s.visible = 1
                GROUP BY s.id, s.name, s.phone, s.address, s.locationCode, s.category, s.rating, s.visible
                ORDER BY s.id
            """)
            salones = cursor.fetchall()
            
            # Para cada salón, obtener sus horarios y reviews
            for salon in salones:
                salon['hours'] = obtener_horarios_salon(salon['id'])
                salon['reviews'] = obtener_reviews_salon(salon['id'])
            
            return salones
    except Error as e:
        print(f"Error al obtener salones: {e}")
        return []



def obtener_todos_salones_admin():
    """Obtiene TODOS los salones (incluyendo ocultos) - solo para admin"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.phone,
                    s.address,
                    s.locationCode,
                    s.category,
                    s.rating,
                    s.visible,
                    COUNT(DISTINCT r.id) as num_reviews
                FROM salones s
                LEFT JOIN reviews r ON s.id = r.salon_id
                GROUP BY s.id, s.name, s.phone, s.address, s.locationCode, s.category, s.rating, s.visible
                ORDER BY s.id
            """)
            salones = cursor.fetchall()
            
            # Para cada salón, obtener sus horarios y reviews
            for salon in salones:
                salon['hours'] = obtener_horarios_salon(salon['id'])
                salon['reviews'] = obtener_reviews_salon(salon['id'])
            
            return salones
    except Error as e:
        print(f"Error al obtener salones: {e}")
        return []



def obtener_salon_por_id(salon_id):
    """Obtiene un salón específico por su ID (solo si está visible)"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    s.id,
                    s.name,
                    s.phone,
                    s.address,
                    s.locationCode,
                    s.category,
                    s.rating,
                    s.visible
                FROM salones s
                WHERE s.id = %s AND s.visible = 1
            """, (salon_id,))
            
            salon = cursor.fetchone()
            
            if salon:
                salon['hours'] = obtener_horarios_salon(salon_id)
                salon['reviews'] = obtener_reviews_salon(salon_id)
            
            return salon
    except Error as e:
        print(f"Error al obtener salón: {e}")
        return None



def obtener_horarios_salon(salon_id):
    """Obtiene los horarios de un salón"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT dia, hora_apertura, hora_cierre, cerrado
                FROM horarios
                WHERE salon_id = %s
                ORDER BY FIELD(dia, 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo')
            """, (salon_id,))
            
            horarios_lista = cursor.fetchall()
            horarios_dict = {}
            
            for h in horarios_lista:
                if h['cerrado']:
                    horarios_dict[h['dia']] = 'Cerrado'
                else:
                    apertura = ''
                    cierre = ''
                    
                    if h['hora_apertura']:
                        if isinstance(h['hora_apertura'], timedelta):
                            total_seconds = int(h['hora_apertura'].total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            apertura = f"{hours:02d}:{minutes:02d}"
                        else:
                            apertura = str(h['hora_apertura'])
                    
                    if h['hora_cierre']:
                        if isinstance(h['hora_cierre'], timedelta):
                            total_seconds = int(h['hora_cierre'].total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            cierre = f"{hours:02d}:{minutes:02d}"
                        else:
                            cierre = str(h['hora_cierre'])
                    
                    if apertura and cierre:
                        horarios_dict[h['dia']] = f"{apertura} - {cierre}"
            
            return horarios_dict if horarios_dict else None
    except Error as e:
        print(f"Error al obtener horarios: {e}")
        return None



# ============================================
# 🆕 FUNCIONES PARA GESTIONAR SALONES
# ============================================



def cambiar_visibilidad_salon(salon_id, visible):
    """Cambia la visibilidad de un salón (ocultar/mostrar)"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE salones
                SET visible = %s
                WHERE id = %s
            """, (visible, salon_id))
            
            if cursor.rowcount > 0:
                estado = "visible" if visible else "oculto"
                print(f"✅ Salón {salon_id} ahora está {estado}")
                return True
            else:
                print(f"⚠️ No se encontró el salón {salon_id}")
                return False
    except Error as e:
        print(f"❌ Error al cambiar visibilidad: {e}")
        return False



def eliminar_salon(salon_id):
    """Elimina un salón y todos sus datos relacionados de forma permanente"""
    try:
        with get_db_cursor(commit=True) as cursor:
            # 1️⃣ Primero eliminar reviews
            cursor.execute("DELETE FROM reviews WHERE salon_id = %s", (salon_id,))
            print(f"✅ Reviews eliminados para salón {salon_id}")
            
            # 2️⃣ Eliminar horarios
            cursor.execute("DELETE FROM horarios WHERE salon_id = %s", (salon_id,))
            print(f"✅ Horarios eliminados para salón {salon_id}")
            
            # 3️⃣ Finalmente eliminar el salón
            cursor.execute("DELETE FROM salones WHERE id = %s", (salon_id,))
            print(f"✅ Salón {salon_id} eliminado permanentemente")
            
            return cursor.rowcount > 0
    except Error as e:
        print(f"❌ Error al eliminar salón: {e}")
        return False



# ============================================
# FUNCIONES PARA REVIEWS
# ============================================



def obtener_reviews_salon(salon_id):
    """Obtiene todos los reviews de un salón"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, nombre, comentario, rating, fecha
                FROM reviews
                WHERE salon_id = %s
                ORDER BY fecha DESC
            """, (salon_id,))
            
            reviews = cursor.fetchall()
            
            # Convertir fecha a string
            for review in reviews:
                review['fecha'] = review['fecha'].strftime('%Y-%m-%d %H:%M:%S')
            
            return reviews
    except Error as e:
        print(f"Error al obtener reviews: {e}")
        return []



def agregar_review(salon_id, nombre, comentario, rating):
    """Agrega un nuevo review y actualiza el rating del salón"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO reviews (salon_id, nombre, comentario, rating)
                VALUES (%s, %s, %s, %s)
            """, (salon_id, nombre, comentario, rating))
            
            review_id = cursor.lastrowid
            
            # Obtener el review insertado
            cursor.execute("""
                SELECT id, nombre, comentario, rating, fecha
                FROM reviews
                WHERE id = %s
            """, (review_id,))
            
            review = cursor.fetchone()
            if review:
                review['fecha'] = review['fecha'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Recalcular rating del salón
            recalcular_promedio_salon(salon_id)
            
            # Obtener el nuevo rating del salón
            cursor.execute("SELECT rating FROM salones WHERE id = %s", (salon_id,))
            salon_data = cursor.fetchone()
            nuevo_rating = float(salon_data['rating']) if salon_data and salon_data['rating'] else None
            
            return review, nuevo_rating
    except Error as e:
        print(f"Error al agregar review: {e}")
        return None, None



def eliminar_review(salon_id, review_id):
    """Elimina un review (solo admin)"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM reviews
                WHERE id = %s AND salon_id = %s
            """, (review_id, salon_id))
            
            # Recalcular el promedio después de eliminar
            if cursor.rowcount > 0:
                recalcular_promedio_salon(salon_id)
            
            return cursor.rowcount > 0
    except Error as e:
        print(f"Error al eliminar review: {e}")
        return False



def actualizar_review(salon_id, review_id, comentario, rating):
    """Actualiza un review existente (solo admin)"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE reviews
                SET comentario = %s, rating = %s
                WHERE id = %s AND salon_id = %s
            """, (comentario, rating, review_id, salon_id))
            
            if cursor.rowcount > 0:
                # Recalcular el promedio después de actualizar
                recalcular_promedio_salon(salon_id)
                
                cursor.execute("""
                    SELECT id, nombre, comentario, rating, fecha
                    FROM reviews
                    WHERE id = %s
                """, (review_id,))
                
                review = cursor.fetchone()
                if review:
                    review['fecha'] = review['fecha'].strftime('%Y-%m-%d %H:%M:%S')
                
                return review
            return None
    except Error as e:
        print(f"Error al actualizar review: {e}")
        return None



def recalcular_promedio_salon(salon_id):
    """Recalcula el promedio de calificaciones de un salón"""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("SELECT AVG(rating) AS promedio FROM reviews WHERE salon_id = %s", (salon_id,))
            resultado = cursor.fetchone()

            nuevo_promedio = round(resultado['promedio'], 1) if resultado['promedio'] is not None else None

            cursor.execute("UPDATE salones SET rating = %s WHERE id = %s", (nuevo_promedio, salon_id))

            return nuevo_promedio
    except Error as e:
        print(f"Error al recalcular promedio: {e}")
        return None



# ============================================
# FUNCIÓN PARA AGREGAR SALONES DESDE SOLICITUDES
# ============================================



def agregar_salon_desde_solicitud(datos, carpeta_fotos):
    """Agrega un nuevo salón desde una solicitud aprobada"""
    try:
        with get_db_cursor(commit=True) as cursor:
            # Insertar el salón (visible = 1 por defecto)
            cursor.execute("""
                INSERT INTO salones (name, phone, address, locationCode, category, rating, visible)
                VALUES (%s, %s, %s, %s, %s, 0, 1)
            """, (
                datos.get('nombre'),
                datos.get('telefono'),
                datos.get('direccion'),
                datos.get('zona', ''),
                datos.get('categoria', 'salones'),
            ))
            
            salon_id = cursor.lastrowid
            
            # Insertar horarios si existen
            horarios = datos.get('horarios', {})
            if horarios:
                for dia, horario in horarios.items():
                    if horario and horario != 'Cerrado':
                        partes = horario.split(' - ')
                        if len(partes) == 2:
                            cursor.execute("""
                                INSERT INTO horarios (salon_id, dia, hora_apertura, hora_cierre, cerrado)
                                VALUES (%s, %s, %s, %s, 0)
                            """, (salon_id, dia, partes[0], partes[1]))
                    else:
                        cursor.execute("""
                            INSERT INTO horarios (salon_id, dia, cerrado)
                            VALUES (%s, %s, 1)
                        """, (salon_id, dia))
            
            return salon_id
    except Error as e:
        print(f"Error al agregar salón desde solicitud: {e}")
        return None



# ============================================
# FUNCIONES PARA ADMINISTRADORES
# ============================================



def verificar_credenciales_admin(email, password):
    """Verifica las credenciales de un administrador"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, email, nombre
                FROM administradores
                WHERE email = %s AND password = %s
            """, (email, password))
            
            admin = cursor.fetchone()
            
            if admin:
                # Actualizar last_login
                with get_db_cursor(commit=True) as update_cursor:
                    update_cursor.execute("""
                        UPDATE administradores
                        SET last_login = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (admin['id'],))
            
            return admin is not None
    except Error as e:
        print(f"Error al verificar credenciales: {e}")
        return False



# ============================================
# FUNCIÓN DE PRUEBA DE CONEXIÓN
# ============================================



def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with get_db_connection() as connection:
            if connection.is_connected():
                print(f"✅ Conectado exitosamente a MySQL Server")
                
                with connection.cursor() as cursor:
                    cursor.execute("SELECT DATABASE();")
                    record = cursor.fetchone()
                    print(f"✅ Conectado a la base de datos: {record[0]}")
                
                return True
    except Error as e:
        print(f"❌ Error de conexión: {e}")
        return False



# ============================================
# EJECUTAR PRUEBA SI SE EJECUTA DIRECTAMENTE
# ============================================



if __name__ == "__main__":
    print("Probando conexión a la base de datos...")
    test_connection()
