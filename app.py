from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import database as db
import os
import json
import shutil



app = Flask(__name__)
app.secret_key = 'kinderfiesta_secret_key_2025'  # Cambiar en producción
CORS(app)



# ============ CONFIGURACIÓN DE SUBIDA DE ARCHIVOS ============
UPLOAD_FOLDER = 'static/solicitudes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB máximo por archivo



# Crear carpetas necesarias
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('data/solicitudes', exist_ok=True)



# Credenciales de administrador
ADMIN_EMAIL = 'admin@kinderfiesta.com'



PALABRAS_PROHIBIDAS = [
    'aborto', 'abortar', 'asno', 'bastardo', 'baboso', 'bobo', 'boludo', 'borracho', 'bruto', 'burro',
    'cabrón', 'cabronazo', 'caca', 'cagada', 'cagado', 'cagón', 'cagar', 'cago', 'calienta huevos', 'carajo',
    'cerdo', 'chupapijas', 'chupamedias', 'chupapolla', 'chupa', 'chúpame', 'chingada', 'chingado', 'chingar', 'chingón',
    'cholo', 'chota', 'choto', 'cochina', 'cochino', 'cojón', 'cojones', 'cojudazo', 'cojudo', 'coludo',
    'conchatumadre', 'concha', 'conchudo', 'cornudo', 'córrete', 'cretino', 'culo', 'culiado', 'culicagado', 'culón',
    'culona', 'culero', 'cursi', 'desgraciado', 'diablos', 'estúpido', 'estúpida', 'feo', 'forro', 'gil',
    'gilipollas', 'gorra', 'grosero', 'grone', 'groncho', 'guarango', 'guevón', 'guevona', 'guevazos', 'hijo de puta',
    'hijoputa', 'hijueputa', 'hijueputas', 'idiota', 'imbécil', 'imbecil', 'infeliz', 'jilipollas', 'jodido', 'joder', 'joto',
    'loco de mierda', 'lameculos', 'lamemierda', 'lamehuevos', 'lamebotas', 'leproso', 'lerdo', 'mala leche', 'malnacido', 'maldito',
    'maldita', 'malparido', 'mamón', 'mamada', 'mamar', 'marica', 'maricón', 'maricona', 'mariconazo', 'mariposón',
    'mierda', 'mierdoso', 'mongólico', 'mongolo', 'mocoso', 'muerto de hambre', 'naco', 'nalgón', 'ojete', 'ojón',
    'pajero', 'pajillero', 'pajote', 'pajuo', 'pajuato', 'pelotudo', 'pendejo', 'pendeja', 'pendejada', 'pendejazo',
    'pene', 'perra', 'perro', 'petardo', 'pezuñas', 'picha', 'pichulón', 'pinche', 'pinga', 'piruja',
    'pirobo', 'pitera', 'pito', 'plasta', 'plomo', 'puta', 'puto', 'putazo', 'putilla', 'putón',
    'putona', 'putear', 'putearse', 'putísima', 'putísimo', 'putañero', 'putañera', 'putero', 'polla', 'pollazo',
    'pichacorta', 'prostituta', 'prostituto', 'rata', 'ratero', 'retrasado', 'ridículo', 'sabandija', 'salame', 'sapazo',
    'sapenco', 'sapo', 'shit', 'sidoso', 'sorete', 'subnormal', 'tarado', 'teta', 'tetona', 'tetón',
    'tontazo', 'tonto', 'tonteja', 'tontillo', 'torpe', 'travesti', 'triplehijueputa', 'triplehijoputa', 'trolo', 'trola',
    'troll', 'vaca', 'vagabunda', 'vagabundo', 'vale verga', 'vergazo', 'verguita', 'verga', 'vergon', 'vergonazo',
    'vieja de mierda', 'viejo pendejo', 'zorra', 'zorrón', 'zorrónazo', 'zángano',
    # amenazas y violencias
    'te voy a matar', 'te mato', 'te voy matar', 'te voy a asesinar', 'te asesino', 'te voy a quemar', 'te quemo',
    'te reviento', 'te revento', 'te parto la cabeza', 'te parto la cara', 'te corto', 'te voy a cortar', 'te destruyo',
    'te voy a destruir', 'voy a matarte', 'voy a matarlo', 'voy a matarla', 'te voy a dar una paliza', 'te doy una paliza',
    'te voy a romper', 'te rompo la cara', 'te prendo fuego', 'te prendo', 'te hundo', 'te ahorco', 'te estrangulo',
    'te hago daño', 'te hago mierda', 'te hago papilla', 'te mando a la mierda', 'me muero por matarte', 'mereces morir',
    'mereces la muerte', 'muérete', 'muerete', 'ojalá mueras', 'ojala que mueras', 'ojalá que te mueras', 'ojalá te mueras',
    'deberías morir', 'mejor que mueras', 'te voy a violar', 'te violaré', 'voy a violarte', 'te voy a violar y matar',
    'vamos a matarte', 'vamos a matarlo', 'vamos a matarla', 'te parto en dos', 'te parto en pedazos', 'te desmembraré',
    'te desmiembro', 'te enterramos vivo', 'te enterramos', 'te atropello', 'te atropello y te mato', 'te pego un tiro',
    'te disparo', 'te ejecuto', 'te ajusticio', 'te degüello', 'te degollo', 'te corto el cuello', 'te corto la cabeza',
    'te decapito', 'te hago picadillo', 'te dejo sin vida', 'sácate la mierda', 'vete a la mierda', 'anda a la mierda',
    'vete al infierno', 'maldito seas', 'maldita seas', 'que te jodan', 'que te den', 'que te den mierda'
]



def filtrar_palabras(texto):
    """Filtra palabras prohibidas reemplazándolas con asteriscos"""
    palabras = texto.split()
    texto_filtrado = []
    for palabra in palabras:
        palabra_lower = palabra.lower()
        censurada = False
        for prohibida in PALABRAS_PROHIBIDAS:
            if prohibida in palabra_lower:
                texto_filtrado.append('*' * len(palabra))
                censurada = True
                break
        if not censurada:
            texto_filtrado.append(palabra)
    return ' '.join(texto_filtrado)



def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




# ============ RUTAS PRINCIPALES ============



@app.route('/')
def index():
    """Página principal con listado de salones"""
    salones = db.obtener_todos_salones()
    return render_template('index.html', salones=salones)




@app.route('/api/salones')
def get_salones():
    """API para obtener todos los salones"""
    salones = db.obtener_todos_salones()
    return jsonify(salones)




@app.route('/api/salon/<int:salon_id>')
def get_salon(salon_id):
    """API para obtener un salón específico"""
    salon = db.obtener_salon_por_id(salon_id)
    if salon:
        return jsonify(salon)
    return jsonify({'error': 'Salón no encontrado'}), 404




@app.route('/api/comentario', methods=['POST'])
def agregar_comentario():
    """Agregar un nuevo comentario y calificación"""
    data = request.json
    salon_id = data.get('salon_id')
    nombre = data.get('nombre', '').strip()
    comentario = data.get('comentario', '').strip()
    rating = data.get('rating')


    # Validaciones
    if not nombre or not comentario or not rating:
        return jsonify({'error': 'Todos los campos son requeridos'}), 400
    if len(comentario) > 500:
        return jsonify({'error': 'El comentario no puede superar los 500 caracteres'}), 400
    if rating < 1 or rating > 5:
        return jsonify({'error': 'La calificación debe estar entre 1 y 5'}), 400


    # Filtrar palabras prohibidas
    comentario_filtrado = filtrar_palabras(comentario)


    # Agregar review a la base de datos
    review, nuevo_rating = db.agregar_review(salon_id, nombre, comentario_filtrado, rating)
    if review:
        return jsonify({'success': True, 'review': review, 'nuevo_rating': nuevo_rating})
    else:
        return jsonify({'error': 'No se pudo agregar el comentario'}), 500




# ============ SISTEMA DE REGISTRO DE LOCALES ============



@app.route('/api/registrar-local', methods=['POST'])
def registrar_local():
    """Recibe y procesa solicitudes de registro de nuevos locales"""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        categoria = request.form.get('categoria', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        direccion = request.form.get('direccion', '').strip()
        zona = request.form.get('zona', '').strip()
        telefono = request.form.get('telefono', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()
        email = request.form.get('email', '').strip()
        google_maps = request.form.get('google_maps', '').strip()
        horarios = json.loads(request.form.get('horarios', '{}'))
        servicios = json.loads(request.form.get('servicios', '[]'))
        
        # Validar campos obligatorios
        if not nombre or not direccion or not telefono:
            return jsonify({
                'success': False,
                'message': 'Los campos Nombre, Dirección y Teléfono son obligatorios'
            }), 400
        
        # Filtrar palabras prohibidas en nombre y descripción
        nombre = filtrar_palabras(nombre)
        descripcion = filtrar_palabras(descripcion)
        
        # Generar ID único para la solicitud
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        solicitud_id = f"solicitud_{timestamp}"
        
        # Crear carpeta para las fotos de esta solicitud
        fotos_folder = os.path.join(UPLOAD_FOLDER, solicitud_id)
        os.makedirs(fotos_folder, exist_ok=True)
        
        # Guardar las fotos
        fotos_guardadas = []
        if 'fotos' in request.files:
            fotos = request.files.getlist('fotos')
            
            # Validar cantidad de fotos
            if len(fotos) < 3:
                return jsonify({
                    'success': False,
                    'message': 'Debes subir al menos 3 fotos de tu local'
                }), 400
            
            if len(fotos) > 5:
                return jsonify({
                    'success': False,
                    'message': 'Máximo 5 fotos permitidas'
                }), 400
            
            for i, foto in enumerate(fotos, 1):
                if foto and allowed_file(foto.filename):
                    # Guardar con nombre secuencial
                    filename = f"{i}.jpg"
                    filepath = os.path.join(fotos_folder, filename)
                    foto.save(filepath)
                    fotos_guardadas.append(filename)
                else:
                    return jsonify({
                        'success': False,
                        'message': f'Formato de imagen no válido. Solo se permiten: {", ".join(ALLOWED_EXTENSIONS)}'
                    }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'Debes subir fotos de tu local'
            }), 400
        
        # Crear objeto de solicitud
        solicitud = {
            'id': solicitud_id,
            'fecha_solicitud': datetime.now().isoformat(),
            'estado': 'pendiente',  # pendiente, aprobado, rechazado
            'datos': {
                'nombre': nombre,
                'categoria': categoria,
                'descripcion': descripcion,
                'direccion': direccion,
                'zona': zona,
                'telefono': telefono,
                'whatsapp': whatsapp,
                'email': email,
                'google_maps': google_maps,
                'horarios': horarios,
                'servicios': servicios,
                'fotos': fotos_guardadas,
                'carpeta_fotos': solicitud_id
            }
        }
        
        # Guardar solicitud en archivo JSON
        solicitudes_file = 'data/solicitudes/solicitudes.json'
        
        # Leer solicitudes existentes
        if os.path.exists(solicitudes_file):
            with open(solicitudes_file, 'r', encoding='utf-8') as f:
                try:
                    solicitudes = json.load(f)
                except json.JSONDecodeError:
                    solicitudes = []
        else:
            solicitudes = []
        
        # Agregar nueva solicitud
        solicitudes.append(solicitud)
        
        # Guardar todas las solicitudes
        with open(solicitudes_file, 'w', encoding='utf-8') as f:
            json.dump(solicitudes, f, indent=4, ensure_ascii=False)
        
        print(f"✅ Nueva solicitud registrada: {solicitud_id}")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud enviada correctamente. Un administrador la revisará pronto.',
            'solicitud_id': solicitud_id
        })
        
    except Exception as e:
        print(f"❌ Error al procesar solicitud: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Error al procesar la solicitud: {str(e)}'
        }), 500




@app.route('/api/admin/solicitudes', methods=['GET'])
def obtener_solicitudes():
    """Obtiene todas las solicitudes (solo para admin)"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        solicitudes_file = 'data/solicitudes/solicitudes.json'
        
        if os.path.exists(solicitudes_file):
            with open(solicitudes_file, 'r', encoding='utf-8') as f:
                solicitudes = json.load(f)
        else:
            solicitudes = []
        
        return jsonify(solicitudes)
        
    except Exception as e:
        print(f"❌ Error al obtener solicitudes: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500




@app.route('/api/solicitud/<solicitud_id>/aprobar', methods=['POST'])
def aprobar_solicitud(solicitud_id):
    """Aprueba una solicitud y la convierte en salón publicado"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        solicitudes_file = 'data/solicitudes/solicitudes.json'
        
        with open(solicitudes_file, 'r', encoding='utf-8') as f:
            solicitudes = json.load(f)
        
        # Buscar la solicitud
        solicitud = next((s for s in solicitudes if s['id'] == solicitud_id), None)
        
        if not solicitud:
            return jsonify({'success': False, 'message': 'Solicitud no encontrada'}), 404
        
        # Agregar el salón a la base de datos
        carpeta_fotos = solicitud['datos'].get('carpeta_fotos', solicitud_id)
        salon_id = db.agregar_salon_desde_solicitud(solicitud['datos'], carpeta_fotos)
        
        if salon_id:
            # Mover fotos de solicitudes a imagenes
            import shutil
            origen = os.path.join('static/solicitudes', carpeta_fotos)
            destino = os.path.join('static/imagenes', carpeta_fotos)
            
            try:
                if os.path.exists(origen):
                    os.makedirs('static/imagenes', exist_ok=True)
                    if os.path.exists(destino):
                        shutil.rmtree(destino)
                    shutil.copytree(origen, destino)
                    print(f"✅ Fotos movidas a: {destino}")
            except Exception as e:
                print(f"⚠️ Error al mover fotos: {e}")
            
            # Marcar como aprobada
            solicitud['estado'] = 'aprobado'
            solicitud['fecha_aprobacion'] = datetime.now().isoformat()
            solicitud['salon_id'] = salon_id
            
            # Guardar cambios
            with open(solicitudes_file, 'w', encoding='utf-8') as f:
                json.dump(solicitudes, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Solicitud aprobada: {solicitud_id} -> Salón ID: {salon_id}")
            
            return jsonify({
                'success': True,
                'message': f'Solicitud aprobada. Salón creado con ID: {salon_id}',
                'salon_id': salon_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al crear el salón en la base de datos'
            }), 500
        
    except Exception as e:
        print(f"❌ Error al aprobar solicitud: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500




@app.route('/api/solicitud/<solicitud_id>/rechazar', methods=['POST'])
def rechazar_solicitud(solicitud_id):
    """Rechaza una solicitud"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        solicitudes_file = 'data/solicitudes/solicitudes.json'
        
        with open(solicitudes_file, 'r', encoding='utf-8') as f:
            solicitudes = json.load(f)
        
        # Buscar la solicitud
        solicitud = next((s for s in solicitudes if s['id'] == solicitud_id), None)
        
        if not solicitud:
            return jsonify({'success': False, 'message': 'Solicitud no encontrada'}), 404
        
        # Marcar como rechazada
        solicitud['estado'] = 'rechazado'
        solicitud['fecha_rechazo'] = datetime.now().isoformat()
        motivo = request.json.get('motivo', 'No especificado')
        solicitud['motivo_rechazo'] = motivo
        
        # Guardar cambios
        with open(solicitudes_file, 'w', encoding='utf-8') as f:
            json.dump(solicitudes, f, indent=4, ensure_ascii=False)
        
        print(f"❌ Solicitud rechazada: {solicitud_id}")
        
        return jsonify({
            'success': True,
            'message': 'Solicitud rechazada'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




# ============ RUTAS DE ADMINISTRACIÓN ============



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Login de administrador"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if db.verificar_credenciales_admin(email, password):
            session['admin_logged_in'] = True
            return redirect(url_for('admin_panel'))
        else:
            return render_template('admin_login.html', error='Credenciales incorrectas')
    return render_template('admin_login.html')




# 🆕 MODIFICADO: Ahora usa obtener_todos_salones_admin()
@app.route('/admin/panel')
def admin_panel():
    """Panel de administración"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    salones = db.obtener_todos_salones_admin()
    return render_template('admin_panel.html', salones=salones)




@app.route('/admin/logout')
def admin_logout():
    """Cerrar sesión de administrador"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))




@app.route('/api/admin/comentario/<int:salon_id>/<int:review_id>', methods=['DELETE'])
def eliminar_comentario(salon_id, review_id):
    """Eliminar un comentario y recalcular el promedio"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401


    if db.eliminar_review(salon_id, review_id):
        # Recalcular el promedio del salón
        nuevo_promedio = db.recalcular_promedio_salon(salon_id)
        return jsonify({'success': True, 'nuevo_promedio': nuevo_promedio})
    else:
        return jsonify({'error': 'No se pudo eliminar el comentario'}), 500




@app.route('/api/admin/comentario/<int:salon_id>/<int:review_id>', methods=['PUT'])
def editar_comentario(salon_id, review_id):
    """Editar un comentario"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401


    data = request.json
    nuevo_comentario = data.get('comentario', '').strip()
    nuevo_rating = data.get('rating')


    if not nuevo_comentario or not nuevo_rating:
        return jsonify({'error': 'Datos incompletos'}), 400
    if len(nuevo_comentario) > 500:
        return jsonify({'error': 'El comentario no puede superar los 500 caracteres'}), 400


    # Filtrar palabras
    nuevo_comentario = filtrar_palabras(nuevo_comentario)
    review = db.actualizar_review(salon_id, review_id, nuevo_comentario, nuevo_rating)


    if review:
        return jsonify({'success': True, 'review': review})
    else:
        return jsonify({'error': 'No se pudo actualizar el comentario'}), 500




# ============ 🆕 NUEVAS RUTAS PARA GESTIONAR SALONES ============



@app.route('/api/verificar-admin', methods=['GET'])
def verificar_admin():
    """Verifica si un administrador está logueado"""
    return jsonify({
        'admin_logged_in': session.get('admin_logged_in', False)
    })



@app.route('/api/admin/salon/<int:salon_id>/visibilidad', methods=['PUT'])
def cambiar_visibilidad(salon_id):
    """Cambia la visibilidad de un salón (ocultar/mostrar)"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.json
        visible = data.get('visible', True)
        
        if db.cambiar_visibilidad_salon(salon_id, visible):
            estado = "visible" if visible else "oculto"
            return jsonify({
                'success': True,
                'message': f'El salón ahora está {estado}',
                'visible': visible
            })
        else:
            return jsonify({'success': False, 'message': 'No se pudo cambiar la visibilidad'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



@app.route('/api/admin/salon/<int:salon_id>', methods=['DELETE'])
def eliminar_salon_route(salon_id):
    """Elimina un salón permanentemente"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        if db.eliminar_salon(salon_id):
            return jsonify({
                'success': True,
                'message': 'El salón fue eliminado correctamente'
            })
        else:
            return jsonify({'success': False, 'message': 'No se pudo eliminar el salón'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




# ============ INICIALIZACIÓN ============



if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 Iniciando KinderFiesta...")
    print("=" * 50)
    if db.test_connection():
        print("✅ Base de datos conectada correctamente")
        print("📁 Carpetas de solicitudes creadas")
        print("=" * 50 + "\n")
        app.run(debug=True, port=5000)
    else:
        print("❌ Error: No se pudo conectar a la base de datos")
        print("Verifica tu configuración en database.py")
        print("=" * 50 + "\n")
