// ===================================
// KINDERFIESTA - JAVASCRIPT PRINCIPAL
// ===================================

let salonActual = null;
let selectedRating = 0;
let fotosSeleccionadas = [];

// ============ INICIALIZACIÓN ============
document.addEventListener('DOMContentLoaded', function () {
    cargarSalones();
    inicializarModal();
    inicializarBuscador();
    inicializarModalRegistro();
});

// ============ CARGAR SALONES ============
async function cargarSalones() {
    try {
        const response = await fetch('/api/salones');
        const salones = await response.json();

        const container = document.getElementById('salones-container');
        container.innerHTML = '';

        salones.forEach(salon => {
            const card = crearTarjetaSalon(salon);
            container.appendChild(card);
        });

        inicializarCarruseles();
    } catch (error) {
        console.error('Error al cargar salones:', error);
    }
}

// ============ CREAR TARJETA DE SALÓN ============
function crearTarjetaSalon(salon) {
    const card = document.createElement('div');
    card.className = 'salon-card';

    const estrellas = generarEstrellas(salon.rating);
    const horariosHTML = salon.hours ? generarHorariosHTML(salon.hours) : '';
    const categoriaHTML = salon.category
        ? `<span class="salon-category">${salon.category}</span>`
        : '';

    const mapaHTML = salon.locationCode
        ? `<a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
              salon.locationCode
          )}" 
            target="_blank" class="btn-mapa">
            <i class="fas fa-map-marker-alt"></i> Ver en mapa
        </a>`
        : '';

    const numReviews = salon.reviews ? salon.reviews.length : 0;
    const carpeta = salon.folder || `salon${salon.id}`;

    const carruselHTML = `
        <div class="carrusel" data-salon="${salon.id}">
            <div class="carrusel-inner">
                ${[1, 2, 3, 4, 5]
                    .map(
                        num => `
                    <div class="carrusel-item">
                        <img src="/static/imagenes/${carpeta}/${num}.jpg" 
                             alt="Imagen ${num} de ${salon.name}" 
                             loading="lazy" 
                             onerror="this.src='/static/img/no-image.png'">
                    </div>
                `
                    )
                    .join('')}
            </div>
            <button class="prev" onclick="moverCarrusel(this, -1)">&#10094;</button>
            <button class="next" onclick="moverCarrusel(this, 1)">&#10095;</button>
        </div>
    `;

    // 🆕 BOTONES DE ADMIN (Solo si está logueado)
    const botonesAdminHTML = `
        <div class="salon-admin-buttons">
            <button class="btn-admin-ocultar" onclick="ocultarSalonPrincipal(${salon.id}, event)" title="Ocultar temporalmente">
                <i class="fas fa-eye-slash"></i>
            </button>
            <button class="btn-admin-eliminar" onclick="eliminarSalonPrincipal(${salon.id}, event)" title="Eliminar permanentemente">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;

    card.innerHTML = `
        <div class="salon-header">
            <h2 class="salon-name">${salon.name}</h2>
            ${categoriaHTML}
        </div>

        ${carruselHTML}

        ${botonesAdminHTML}

        <div class="salon-info">
            <div class="info-item">
                <i class="fas fa-map-marker-alt"></i>
                <span class="salon-direccion">${salon.address}</span>
            </div>

            ${
                salon.phone
                    ? `
            <div class="info-item">
                <i class="fas fa-phone"></i>
                <a href="tel:${salon.phone}">${salon.phone}</a>
            </div>`
                    : ''
            }

            ${horariosHTML}

            <div class="rating-display">
                ${
                    salon.rating
                        ? `
                    <div class="stars">${estrellas}</div>
                    <span class="rating-number">${salon.rating}</span>
                    <span style="color: #999; margin-left: 5px;">(${numReviews} ${
                              numReviews === 1 ? 'reseña' : 'reseñas'
                          })</span>
                `
                        : `<span class="no-rating">Sin calificaciones aún</span>`
                }
            </div>

            ${mapaHTML}
        </div>

        <button class="btn-comentar" onclick="abrirModalComentarios(${salon.id})">
            <i class="fas fa-comment"></i> Ver comentarios y calificar
        </button>
    `;

    // 🆕 Mostrar/Ocultar botones de admin según sesión
    verificarSesionAdmin(card);

    return card;
}

// 🆕 VERIFICAR SI ADMIN ESTÁ LOGUEADO
function verificarSesionAdmin(card) {
    fetch('/api/verificar-admin')
        .then(response => response.json())
        .then(data => {
            if (!data.admin_logged_in) {
                const botonesAdmin = card.querySelector('.salon-admin-buttons');
                if (botonesAdmin) {
                    botonesAdmin.style.display = 'none';
                }
            }
        })
        .catch(error => {
            // Si hay error, ocultamos los botones por seguridad
            const botonesAdmin = card.querySelector('.salon-admin-buttons');
            if (botonesAdmin) {
                botonesAdmin.style.display = 'none';
            }
        });
}

// 🆕 OCULTAR SALÓN TEMPORALMENTE
function ocultarSalonPrincipal(salonId, event) {
    event.stopPropagation();
    
    Swal.fire({
        title: '¿Ocultar este salón?',
        text: 'El salón estará oculto temporalmente en la página principal',
        icon: 'question',
        showCancelButton: true,
        confirmButtonText: '👁️ Sí, ocultar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#3498db',
        cancelButtonColor: '#95a5a6'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/api/admin/salon/${salonId}/visibilidad`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ visible: false })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: 'Salón oculto',
                        text: 'El salón ha sido ocultado temporalmente',
                        icon: 'success',
                        confirmButtonColor: '#3498db',
                        timer: 2000
                    });
                    cargarSalones();
                } else {
                    Swal.fire('Error', data.message || 'No se pudo ocultar el salón', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'No se pudo ocultar el salón', 'error');
            });
        }
    });
}

// 🆕 ELIMINAR SALÓN PERMANENTEMENTE
function eliminarSalonPrincipal(salonId, event) {
    event.stopPropagation();
    
    Swal.fire({
        title: '⚠️ ¿Eliminar este salón permanentemente?',
        text: 'Esta acción no se puede deshacer',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: '🗑️ Sí, eliminar',
        cancelButtonText: 'Cancelar',
        confirmButtonColor: '#e74c3c',
        cancelButtonColor: '#95a5a6'
    }).then(result => {
        if (result.isConfirmed) {
            fetch(`/api/admin/salon/${salonId}`, {
                method: 'DELETE',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire({
                        title: '¡Eliminado!',
                        text: 'El salón ha sido eliminado permanentemente',
                        icon: 'success',
                        confirmButtonColor: '#27ae60',
                        timer: 2000
                    });
                    cargarSalones();
                } else {
                    Swal.fire('Error', data.message || 'No se pudo eliminar el salón', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire('Error', 'No se pudo eliminar el salón', 'error');
            });
        }
    });
}

// ============ FUNCIONES DEL CARRUSEL ============
function inicializarCarruseles() {
    document.querySelectorAll('.carrusel-inner').forEach(inner => {
        if (inner.children.length > 0) inner.children[0].classList.add('activo');
    });
}

function moverCarrusel(btn, dir) {
    const carruselInner = btn.parentElement.querySelector('.carrusel-inner');
    const items = carruselInner.children;
    if (!items.length) return;
    const total = items.length;

    let indexActual = [...items].findIndex(item =>
        item.classList.contains('activo')
    );

    items[indexActual].classList.remove('activo');
    indexActual = (indexActual + dir + total) % total;
    items[indexActual].classList.add('activo');
}

// ============ GENERAR ESTRELLAS ============
function generarEstrellas(rating) {
    if (!rating) return '';

    const estrellaLlena = '<i class="fas fa-star"></i>';
    const estrellaVacia = '<i class="far fa-star"></i>';
    const estrellaMedia = '<i class="fas fa-star-half-alt"></i>';

    let html = '';
    const ratingEntero = Math.floor(rating);
    const tieneMedia = rating % 1 >= 0.5;

    for (let i = 0; i < ratingEntero; i++) html += estrellaLlena;
    if (tieneMedia && ratingEntero < 5) html += estrellaMedia;
    const estrellasVacias = 5 - Math.ceil(rating);
    for (let i = 0; i < estrellasVacias; i++) html += estrellaVacia;

    return html;
}

// ============ GENERAR HORARIOS HTML ============
function generarHorariosHTML(hours) {
    const dias = [
        'lunes',
        'martes',
        'miércoles',
        'jueves',
        'viernes',
        'sábado',
        'domingo'
    ];
    let html = '<div class="horarios"><h4><i class="fas fa-clock"></i> Horarios</h4>';

    dias.forEach(dia => {
        if (hours[dia]) {
            html += `
                <div class="horario-item">
                    <span class="horario-dia">${dia.charAt(0).toUpperCase() + dia.slice(1)}:</span>
                    <span class="horario-hora">${hours[dia]}</span>
                </div>
            `;
        }
    });

    html += '</div>';
    return html;
}

// ============ MODAL DE COMENTARIOS ============
function abrirModalComentarios(salonId) {
    salonActual = salonId;

    fetch(`/api/salon/${salonId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('modal-salon-nombre').textContent =
                `Comentarios - ${data.name || 'Salón'}`;

            const comentariosLista = document.getElementById('comentarios-lista');
            comentariosLista.innerHTML = '';

            if (data.reviews && data.reviews.length > 0) {
                data.reviews.forEach(review => {
                    const reviewHTML = `
                        <div class="comentario-item">
                            <div class="comentario-header">
                                <span class="comentario-autor">${review.nombre}</span>
                                <div class="stars">${generarEstrellas(review.rating)}</div>
                            </div>
                            <p class="comentario-texto">${review.comentario}</p>
                        </div>
                    `;
                    comentariosLista.innerHTML += reviewHTML;
                });
            } else {
                comentariosLista.innerHTML = '<p class="no-comentarios">No hay comentarios aún. ¡Sé el primero en comentar!</p>';
            }

            resetearFormulario();
            document.getElementById('modal-comentarios').classList.add('active');
            setTimeout(inicializarEstrellas, 100);
        })
        .catch(error => {
            console.error('Error al cargar comentarios:', error);
            alert('Error al cargar los comentarios. Por favor, intenta de nuevo.');
        });
}

function resetearFormulario() {
    document.getElementById('comentario-nombre').value = '';
    document.getElementById('comentario-texto').value = '';

    const stars = document.querySelectorAll('.star-rating .star');
    stars.forEach(star => star.classList.remove('active'));
    selectedRating = 0;

    const counter = document.getElementById('char-counter');
    if (counter) {
        counter.textContent = '0/500';
        counter.classList.remove('warning', 'error');
    }
}

function inicializarEstrellas() {
    const stars = document.querySelectorAll('.star-rating .star');

    stars.forEach(star => {
        const newStar = star.cloneNode(true);
        star.parentNode.replaceChild(newStar, star);
    });

    const newStars = document.querySelectorAll('.star-rating .star');
    newStars.forEach(star => {
        star.addEventListener('click', function () {
            const rating = parseInt(this.getAttribute('data-rating'));
            selectedRating = rating;

            newStars.forEach(s => s.classList.remove('active'));
            for (let i = 0; i < rating; i++) {
                newStars[i].classList.add('active');
            }
        });

        star.addEventListener('mouseenter', function () {
            const rating = parseInt(this.getAttribute('data-rating'));
            newStars.forEach((s, index) => {
                if (index < rating) {
                    s.style.color = '#ffcc00';
                    s.style.transform = 'scale(1.2)';
                }
            });
        });

        star.addEventListener('mouseleave', function () {
            newStars.forEach((s, index) => {
                if (!s.classList.contains('active')) {
                    s.style.color = '';
                    s.style.transform = '';
                }
            });
        });
    });
}

function inicializarModal() {
    const closeBtn = document.querySelector('.close-modal');
    if (closeBtn) {
        closeBtn.addEventListener('click', function () {
            document.getElementById('modal-comentarios').classList.remove('active');
        });
    }

    const modal = document.getElementById('modal-comentarios');
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    const textarea = document.getElementById('comentario-texto');
    const counter = document.getElementById('char-counter');

    if (textarea && counter) {
        textarea.addEventListener('input', function () {
            const length = this.value.length;
            const remaining = 500 - length;

            counter.textContent = `${length}/500`;
            counter.classList.remove('warning', 'error');

            if (remaining < 50 && remaining >= 0) {
                counter.classList.add('warning');
            } else if (remaining < 0) {
                counter.classList.add('error');
            }
        });
    }
}

function enviarComentario() {
    const nombre = document.getElementById('comentario-nombre').value.trim();
    const comentario = document.getElementById('comentario-texto').value.trim();

    if (!nombre) {
        alert('Por favor, ingresa tu nombre.');
        return;
    }

    if (!comentario) {
        alert('Por favor, escribe un comentario.');
        return;
    }

    if (selectedRating === 0) {
        alert('Por favor, selecciona una calificación (estrellas).');
        return;
    }

    if (comentario.length > 500) {
        alert('El comentario no puede exceder los 500 caracteres.');
        return;
    }

    const btnEnviar = document.querySelector('.btn-enviar');
    const textoOriginal = btnEnviar.innerHTML;
    btnEnviar.disabled = true;
    btnEnviar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

    fetch('/api/comentario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            salon_id: salonActual,
            nombre: nombre,
            comentario: comentario,
            rating: selectedRating
        })
    })
        .then(response => response.json())
        .then(data => {
            btnEnviar.disabled = false;
            btnEnviar.innerHTML = textoOriginal;

            if (data.success) {
                alert('¡Comentario enviado exitosamente!');
                document.getElementById('modal-comentarios').classList.remove('active');
                cargarSalones();
            } else {
                alert('Error al enviar el comentario: ' + (data.message || 'Intenta de nuevo.'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            btnEnviar.disabled = false;
            btnEnviar.innerHTML = textoOriginal;
            alert('Error de conexión. Por favor, verifica tu internet e intenta de nuevo.');
        });
}

// ===============================================
// 🔍 BUSCADOR DE SALONES
// ===============================================
function inicializarBuscador() {
    const inputBuscador = document.getElementById('buscador-input');
    const btnBuscar = document.getElementById('btn-buscar');
    if (!inputBuscador) return;

    inputBuscador.addEventListener('input', aplicarBusqueda);
    if (btnBuscar) btnBuscar.addEventListener('click', aplicarBusqueda);
    inputBuscador.addEventListener('keypress', e => {
        if (e.key === 'Enter') aplicarBusqueda();
    });
}

function normalizarTexto(texto) {
    return texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

function aplicarBusqueda() {
    const termino = normalizarTexto(document.getElementById("buscador-input").value);
    const cards = document.querySelectorAll(".salon-card");

    let encontrados = 0;
    cards.forEach(card => {
        const nombre = normalizarTexto(card.querySelector(".salon-name")?.textContent || "");
        const direccion = normalizarTexto(card.querySelector(".salon-direccion")?.textContent || "");
        const visible = nombre.includes(termino) || direccion.includes(termino);
        
        card.style.display = visible ? "block" : "none";
        card.style.transition = "all 0.3s ease";
        card.style.opacity = visible ? "1" : "0";
        
        if (visible) encontrados++;
    });

    // Mostrar mensaje si no hay resultados
    const container = document.getElementById('salones-container');
    let noResultados = container.querySelector('.no-resultados');
    
    if (encontrados === 0 && termino) {
        if (!noResultados) {
            noResultados = document.createElement('div');
            noResultados.className = 'no-resultados';
            noResultados.innerHTML = `
                <i class="fas fa-search"></i>
                <p>No se encontraron resultados para "${document.getElementById("buscador-input").value}"</p>
                <button onclick="limpiarBusqueda()" class="btn-limpiar">
                    <i class="fas fa-times"></i> Limpiar búsqueda
                </button>
            `;
            container.appendChild(noResultados);
        }
    } else if (noResultados) {
        noResultados.remove();
    }
}

function buscarSalones() {
    aplicarBusqueda();
}

function limpiarBusqueda() {
    document.getElementById('buscador-input').value = '';
    aplicarBusqueda();
}

// ===============================================
// 📝 SISTEMA DE REGISTRO DE LOCAL
// ===============================================

function inicializarModalRegistro() {
    const modal = document.getElementById('modal-registro');
    const closeBtn = document.querySelector('.close-modal-registro');
    
    if (closeBtn) {
        closeBtn.addEventListener('click', cerrarModalRegistro);
    }
    
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                cerrarModalRegistro();
            }
        });
    }
}

function abrirModalRegistro() {
    const modal = document.getElementById('modal-registro');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden'; // Evitar scroll del body
}

function cerrarModalRegistro() {
    const modal = document.getElementById('modal-registro');
    modal.classList.remove('active');
    document.body.style.overflow = ''; // Restaurar scroll
    limpiarFormularioRegistro();
}

function limpiarFormularioRegistro() {
    document.getElementById('form-registro').reset();
    fotosSeleccionadas = [];
    document.getElementById('preview-fotos').innerHTML = '';
}

// ============ PREVISUALIZAR FOTOS ============
function previsualizarFotos(input) {
    const files = Array.from(input.files);
    const previewContainer = document.getElementById('preview-fotos');
    
    // Validar número de fotos
    if (files.length < 3) {
        alert('Por favor, selecciona al menos 3 fotos de tu local.');
        input.value = '';
        return;
    }
    
    if (files.length > 5) {
        alert('Máximo 5 fotos permitidas.');
        input.value = '';
        return;
    }
    
    // Validar tamaño de archivos
    const maxSize = 5 * 1024 * 1024; // 5MB
    for (let file of files) {
        if (file.size > maxSize) {
            alert(`La foto "${file.name}" excede el tamaño máximo de 5MB.`);
            input.value = '';
            previewContainer.innerHTML = '';
            return;
        }
    }
    
    fotosSeleccionadas = files;
    previewContainer.innerHTML = '';
    
    files.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function(e) {
            const previewItem = document.createElement('div');
            previewItem.className = 'preview-item';
            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="Foto ${index + 1}">
                <button type="button" class="btn-eliminar-foto" onclick="eliminarFoto(${index})">
                    <i class="fas fa-times"></i>
                </button>
                <span class="foto-numero">${index + 1}</span>
            `;
            previewContainer.appendChild(previewItem);
        };
        reader.readAsDataURL(file);
    });
}

function eliminarFoto(index) {
    const input = document.getElementById('reg-fotos');
    const dt = new DataTransfer();
    
    fotosSeleccionadas.forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    input.files = dt.files;
    fotosSeleccionadas = Array.from(dt.files);
    
    if (fotosSeleccionadas.length > 0) {
        previsualizarFotos(input);
    } else {
        document.getElementById('preview-fotos').innerHTML = '';
    }
}

// ============ ENVIAR REGISTRO ============
async function enviarRegistro(event) {
    event.preventDefault();
    
    // Validar fotos
    if (fotosSeleccionadas.length < 3) {
        alert('Por favor, sube al menos 3 fotos de tu local.');
        return;
    }
    
    // Recopilar datos del formulario
    const formData = new FormData();
    
    // Información básica
    formData.append('nombre', document.getElementById('reg-nombre').value);
    formData.append('categoria', document.getElementById('reg-categoria').value);
    formData.append('descripcion', document.getElementById('reg-descripcion').value);
    
    // Ubicación y contacto
    formData.append('direccion', document.getElementById('reg-direccion').value);
    formData.append('zona', document.getElementById('reg-zona').value);
    formData.append('telefono', document.getElementById('reg-telefono').value);
    formData.append('whatsapp', document.getElementById('reg-whatsapp').value);
    formData.append('email', document.getElementById('reg-email').value);
    formData.append('google_maps', document.getElementById('reg-google-maps').value);
    
    // Horarios
    const horarios = {};
    const dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'];
    dias.forEach(dia => {
        const checkbox = document.getElementById(`check-${dia}`);
        const input = document.getElementById(`reg-${dia}`);
        if (checkbox && checkbox.checked && input && input.value) {
            horarios[dia] = input.value;
        }
    });
    formData.append('horarios', JSON.stringify(horarios));
    
    // Servicios
    const servicios = [];
    document.querySelectorAll('.servicio-check:checked').forEach(checkbox => {
        servicios.push(checkbox.value);
    });
    formData.append('servicios', JSON.stringify(servicios));
    
    // Fotos
    fotosSeleccionadas.forEach((foto, index) => {
        formData.append('fotos', foto, `foto_${index + 1}.jpg`);
    });
    
    // Mostrar indicador de carga
    const btnSubmit = document.querySelector('.btn-enviar-registro');
    const textoOriginal = btnSubmit.innerHTML;
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando solicitud...';
    
    try {
        const response = await fetch('/api/registrar-local', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('¡Solicitud enviada exitosamente! Un administrador revisará tu solicitud pronto.');
            cerrarModalRegistro();
            limpiarFormularioRegistro();
        } else {
            alert('Error al enviar la solicitud: ' + (data.message || 'Intenta de nuevo.'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error de conexión. Por favor, verifica tu internet e intenta de nuevo.');
    } finally {
        btnSubmit.disabled = false;
        btnSubmit.innerHTML = textoOriginal;
    }
}
