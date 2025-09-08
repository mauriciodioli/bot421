
// ===== Config / Utils =====
const STORAGE_PREFIX = 'dpia:reseñas';

function getStorageKey() {
  // Busca un ID de publicación si existe en el DOM
  const el = document.querySelector('[data-publicacion-id]');
  const pubId = el?.dataset?.publicacionId || 'home';
  return `${STORAGE_PREFIX}:${pubId}`;
}

function leerReseñas() {
  const key = getStorageKey();
  try {
    return JSON.parse(localStorage.getItem(key)) || [];
  } catch (_) {
    return [];
  }
}

function guardarReseñas(arr) {
  const key = getStorageKey();
  localStorage.setItem(key, JSON.stringify(arr || []));
}

// ===== Datos fijos opcionales =====
const reseñasFijas = [
  { nombre: "Juan Pérez",  comentario: "Excelente producto, superó mis expectativas." },
  { nombre: "María López", comentario: "Entrega rápida y atención al cliente impecable." }
];

// ===== Arranque =====
document.addEventListener('DOMContentLoaded', function () {
  const form = document.getElementById('form-reseña');
  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');

  // Si no hay usuario logueado, ocultar el form si existe
  if (form && (!userId || !correo)) {
    form.style.display = 'none';
  }

  // Listener de submit (si existe el form en la página)
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const nombre = document.getElementById('nombre-reseña')?.value.trim();
      const comentario = document.getElementById('comentario-reseña')?.value.trim();
      if (!nombre || !comentario) return;

      const nuevas = leerReseñas();
      const userId = localStorage.getItem('usuario_id');
      const correo = localStorage.getItem('correo_electronico');

      nuevas.push({
        nombre,
        comentario,
        fecha: new Date().toISOString(),
        user_id: userId || null,
        correo_electronico: correo || null
      });

      guardarReseñas(nuevas);
      form.reset();
      cargarReseñas();
    });
  }

  cargarReseñas();
});

// ===== Render =====
function cargarReseñas() {
  const contenedor = document.getElementById('contenedor-reseñas');
  const mensaje = document.getElementById('mensaje-sin-reseñas');
  if (!contenedor || !mensaje) return; // evitar nulls

  const data = leerReseñas();

  contenedor.innerHTML = '';

  // Si querés “sembrar” reseñas fijas cuando no hay nada:
  const fuente = (data.length ? data : []).slice(); // clonar
  if (fuente.length === 0 && Array.isArray(reseñasFijas)) {
    // mostrar fijas solo visualmente (no las guardo en localStorage)
    fuente.push(...reseñasFijas.map(r => ({ ...r, fecha: null, user_id: null })));
  }

  if (fuente.length === 0) {
    mensaje.style.display = 'block';
    return;
  }

  mensaje.style.display = 'none';

  const ordenadas = ordenarPorFechaDescendente(fuente);
  const primerasTres = ordenadas.slice(0, 3);
  const restantes = ordenadas.slice(3);

  primerasTres.forEach((r, i) => {
    contenedor.innerHTML += generarHTMLReseña(r, i);
  });

  if (restantes.length > 0) {
    contenedor.innerHTML += generarDesplegableReseñas('reseñas-extra', restantes, 3);
  }
}

function eliminarReseña(index) {
  const reseñas = leerReseñas();
  reseñas.splice(index, 1);
  guardarReseñas(reseñas);
  cargarReseñas();
}

function editarReseña(index) {
  const reseñas = leerReseñas();
  const nuevaNombre = prompt("Editar nombre:", reseñas[index]?.nombre ?? '');
  const nuevoComentario = prompt("Editar comentario:", reseñas[index]?.comentario ?? '');

  if (nuevaNombre && nuevoComentario) {
    reseñas[index].nombre = nuevaNombre;
    reseñas[index].comentario = nuevoComentario;
    guardarReseñas(reseñas);
    cargarReseñas();
  }
}

function ordenarPorFechaDescendente(reseñas) {
  // Si no hay fecha (p.ej. las fijas), las manda al final
  return reseñas.slice().sort((a, b) => {
    const fechaA = a.fecha ? new Date(a.fecha).getTime() : -Infinity;
    const fechaB = b.fecha ? new Date(b.fecha).getTime() : -Infinity;
    return fechaB - fechaA;
  });
}

function generarHTMLReseña(r, index) {
  const fechaFormateada = r.fecha
    ? new Date(r.fecha).toLocaleString('es-AR')
    : '';

  const userId = localStorage.getItem('usuario_id');
  const correo = localStorage.getItem('correo_electronico');
  const esAutor = r.user_id && r.correo_electronico &&
                  r.user_id === userId && r.correo_electronico === correo;

  const botones = esAutor
    ? `
      <div class="acciones-reseña">
        <button class="icono-btn" onclick="editarReseña(${index})" title="Editar reseña">✏️</button>
        <button class="icono-btn" onclick="eliminarReseña(${index})" title="Eliminar reseña">🗑️</button>
      </div>`
    : '';

  return `
    <div class="testimonial">
      ${fechaFormateada ? `<small>${fechaFormateada}</small>` : ''}
      <p>"${r.comentario ?? ''}"</p>
      <h4>- ${r.nombre ?? 'Anónimo'}</h4>
      ${botones}
    </div>`;
}

function generarDesplegableReseñas(id, reseñasOcultas, offset = 0) {
  const contenido = reseñasOcultas.map((r, i) => generarHTMLReseña(r, i + offset)).join('');
  return `
    <button type="button" onclick="toggleReseñas('${id}', this)">Mostrar más reseñas</button>
    <div id="${id}" style="display:none;">
      ${contenido}
    </div>`;
}

function toggleReseñas(id, boton) {
  const div = document.getElementById(id);
  if (!div) return;
  const visible = div.style.display === 'block';
  div.style.display = visible ? 'none' : 'block';
  boton.textContent = visible ? 'Mostrar más reseñas' : 'Ocultar reseñas';
}

