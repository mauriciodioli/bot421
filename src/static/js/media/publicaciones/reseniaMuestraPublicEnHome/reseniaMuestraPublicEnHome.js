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

// === Cookies / Idioma ===
function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function normalizarIdioma(raw) {
  const v = (raw || '').toLowerCase();
  const base = v.split('-')[0]; // es-ES -> es
  // tu app a veces guarda 'in' para inglés
  if (base === 'in') return 'en';
  return base || 'es';
}

// >>> ===== RNG determinístico por publicación =====
// Hash djb2 string -> uint32
function hashStr(s) {
  let h = 5381;
  for (let i = 0; i < s.length; i++) h = ((h << 5) + h) + s.charCodeAt(i);
  return h >>> 0;
}
// PRNG simple (mulberry32)
function mulberry32(seed) {
  return function () {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
// Fisher–Yates con RNG inyectado
function shuffleDeterministico(arr, rng) {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Selección estable por idioma + publicacion_id
function seleccionarReseñasFijasParaPublicacion(idioma, pubId, maxN = 7) {
  // ✅ usar la variable global (const) directamente, no window.*
  const base = (reseñasFijas && reseñasFijas[idioma])
            || (reseñasFijas && reseñasFijas.es)
            || [];
  if (!base.length) return [];

  const rng = mulberry32(hashStr(`${idioma}|${pubId}`));
  const n = Math.max(3, Math.min(maxN, Math.floor(rng() * (maxN - 2)) + 3));
  return shuffleDeterministico(base, rng).slice(0, Math.min(n, base.length));
}

// <<< ===== RNG determinístico por publicación =====

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

  // Idioma desde cookie (normalizado) con fallback 'es'
  const idiomaCookie = normalizarIdioma(getCookie('language')) || 'es';

  // >>> reemplazo del “sembrado” para que varíe por publicación
  let fuente = (data.length ? data : []).slice(); // clonar
  if (fuente.length === 0) {
    const pubId = document.querySelector('[data-publicacion-id]')?.dataset?.publicacionId || 'home';
    const pack = seleccionarReseñasFijasParaPublicacion(idiomaCookie, pubId);
    // mostrar fijas solo visualmente (no las guardo en localStorage)
    fuente.push(...pack.map(r => ({ ...r, fecha: null, user_id: null })));
  }
  // <<< reemplazo del “sembrado”

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
  const lang = normalizarIdioma(getCookie('language')) || 'es';
  const fechaFormateada = r.fecha
    ? new Date(r.fecha).toLocaleString(lang)
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

// Helper para texto según idioma
function tReseñas(key) {
  const lang = normalizarIdioma(getCookie('language')) || 'es';
  return (textosReseñas[lang] && textosReseñas[lang][key]) 
         || textosReseñas['es'][key];
}

// ===== Render botón desplegable =====
function generarDesplegableReseñas(id, reseñasOcultas, offset = 0) {
  const contenido = reseñasOcultas.map((r, i) => generarHTMLReseña(r, i + offset)).join('');
  return `
    <button type="button" onclick="toggleReseñas('${id}', this)">${tReseñas('verMas')}</button>
    <div id="${id}" style="display:none;">
      ${contenido}
    </div>`;
}

function toggleReseñas(id, boton) {
  const div = document.getElementById(id);
  if (!div) return;
  const visible = div.style.display === 'block';
  div.style.display = visible ? 'none' : 'block';
  boton.textContent = visible ? tReseñas('verMas') : tReseñas('ocultar');
}


// ===== Datos fijos opcionales =====
const reseñasFijas = {
  es: [
    { nombre: "Juan Pérez",        comentario: "Excelente , superó mis expectativas." },
    { nombre: "María López",       comentario: "Entrega rápida y atención al cliente impecable." },
    { nombre: "Sofía Ramírez",     comentario: "Muy buena calidad; se nota el cuidado. Lo volvería a comprar." },
    { nombre: "Carlos Gómez",      comentario: "Funciona perfecto desde el primer día." },
    { nombre: "Luciana Fernández", comentario: "Gran relación precio/calidad." },
    { nombre: "Andrés Molina",     comentario: "El empaque llegó intacto y a tiempo." },
    { nombre: "Valentina Torres",  comentario: "Soporte técnico respondió en minutos." }
  ],
  en: [
    { nombre: "John Smith",     comentario: "Excellent product, exceeded my expectations." },
    { nombre: "Mary Johnson",   comentario: "Fast delivery and outstanding customer service." },
    { nombre: "Sophia Brown",   comentario: "Top quality; would buy again." },
    { nombre: "Charles Miller", comentario: "Works flawlessly from day one." },
    { nombre: "Emily Davis",    comentario: "Great value for money." },
    { nombre: "Andrew Wilson",  comentario: "Packaging was perfect and on time." },
    { nombre: "Olivia Taylor",  comentario: "Tech support replied within minutes." }
  ],
  pl: [
    { nombre: "Jan Kowalski",          comentario: "Świetny produkt, przekroczył moje oczekiwania." },
    { nombre: "Maria Nowak",           comentario: "Szybka dostawa i doskonała obsługa klienta." },
    { nombre: "Zofia Wiśniewska",      comentario: "Bardzo dobra jakość; kupię ponownie." },
    { nombre: "Karol Lewandowski",     comentario: "Działa bez zarzutu od pierwszego dnia." },
    { nombre: "Agnieszka Zielińska",   comentario: "Świetny stosunek jakości do ceny." },
    { nombre: "Piotr Kamiński",        comentario: "Opakowanie bez uszkodzeń, dostarczone na czas." },
    { nombre: "Katarzyna Dąbrowska",   comentario: "Wsparcie techniczne odpowiedziało w kilka minut." }
  ],
  it: [
    { nombre: "Giovanni Rossi",  comentario: "Prodotto eccellente, ha superato le mie aspettative." },
    { nombre: "Maria Bianchi",   comentario: "Consegna rapida e servizio clienti impeccabile." },
    { nombre: "Sofia Romano",    comentario: "Ottima qualità; lo ricomprerò." },
    { nombre: "Carlo Esposito",  comentario: "Funziona perfettamente dal primo giorno." },
    { nombre: "Giulia Conti",    comentario: "Ottimo rapporto qualità/prezzo." },
    { nombre: "Andrea Moretti",  comentario: "Imballaggio perfetto e puntuale." },
    { nombre: "Chiara Greco",    comentario: "L’assistenza ha risposto in pochi minuti." }
  ],
  fr: [
    { nombre: "Jean Dupont",       comentario: "Produit excellent, a dépassé mes attentes." },
    { nombre: "Marie Martin",      comentario: "Livraison rapide et service client impeccable." },
    { nombre: "Sophie Bernard",    comentario: "Très bonne qualité ; j’achèterai à nouveau." },
    { nombre: "Charles Laurent",   comentario: "Fonctionne parfaitement dès le premier jour." },
    { nombre: "Camille Durand",    comentario: "Excellent rapport qualité-prix." },
    { nombre: "Antoine Moreau",    comentario: "Emballage nickel et livraison à l’heure." },
    { nombre: "Élise Lefèvre",     comentario: "Le support a répondu en quelques minutes." }
  ],
  pt: [
    { nombre: "João Silva",       comentario: "Produto excelente, superou minhas expectativas." },
    { nombre: "Maria Santos",     comentario: "Entrega rápida e atendimento impecável." },
    { nombre: "Sofia Almeida",    comentario: "Ótima qualidade; compraria novamente." },
    { nombre: "Carlos Pereira",   comentario: "Funciona perfeitamente desde o primeiro dia." },
    { nombre: "Ana Oliveira",     comentario: "Ótimo custo-benefício." },
    { nombre: "André Costa",      comentario: "Embalagem perfeita e entrega pontual." },
    { nombre: "Beatriz Souza",    comentario: "Suporte técnico respondeu em minutos." }
  ],
  de: [
    { nombre: "Max Müller",        comentario: "Ausgezeichnetes Produkt, hat meine Erwartungen übertroffen." },
    { nombre: "Maria Schmidt",     comentario: "Schnelle Lieferung und hervorragender Kundenservice." },
    { nombre: "Sophie Schneider",  comentario: "Sehr gute Qualität; würde wieder kaufen." },
    { nombre: "Karl Fischer",      comentario: "Funktioniert seit dem ersten Tag einwandfrei." },
    { nombre: "Lukas Wagner",      comentario: "Gutes Preis-Leistungs-Verhältnis." },
    { nombre: "Anna Weber",        comentario: "Verpackung war einwandfrei und pünktlich." },
    { nombre: "Leon Becker",       comentario: "Der Support antwortete innerhalb weniger Minuten." }
  ]
};


// ===== Diccionario i18n para el botón "Mostrar más reseñas" =====
const textosReseñas = {
  es: { verMas: "Mostrar más reseñas", ocultar: "Ocultar reseñas" },
  en: { verMas: "Show more reviews",   ocultar: "Hide reviews" },
  pl: { verMas: "Pokaż więcej opinii", ocultar: "Ukryj opinie" },
  it: { verMas: "Mostra più recensioni", ocultar: "Nascondi recensioni" },
  fr: { verMas: "Afficher plus d’avis",  ocultar: "Masquer les avis" },
  pt: { verMas: "Mostrar mais avaliações", ocultar: "Ocultar avaliações" },
  de: { verMas: "Mehr Bewertungen anzeigen", ocultar: "Bewertungen ausblenden" }
};


// ✅ agrega esta línea:
window.reseñasFijas = reseñasFijas;