async function cargarWhatsappDeUsuarioPOST() {
  const raw = localStorage.getItem('usuario_id');
  const userId = raw ? parseInt(raw, 10) : NaN;
  if (!Number.isInteger(userId) || userId <= 0) return;

  const res = await fetch('/social-chats-whatssapp/whatsapp/primary/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
      // 'X-CSRFToken': getCookie('csrf_token')  // si usás CSRF
    },
    credentials: 'same-origin',
    body: JSON.stringify({ user_id: userId })
  });
 
  if (!res.ok) return;                   // si no hay, no guardes nada (404)
  const data = await res.json();
  const tel = data?.valor?.trim();
  if (!tel) return;

  localStorage.setItem(`numTelefono:${userId}`, tel);
}

document.addEventListener('DOMContentLoaded', cargarWhatsappDeUsuarioPOST);













async function guardarTelefonoWhatsApp() {
  const ownerId  = localStorage.getItem('usuario_id');
  if (!ownerId) {
    alert('Iniciá sesión para guardar tu número de WhatsApp.');
    return;
  }
  

const pubIdRaw = localStorage.getItem('publicacion_id') || '';
const dominio_id = localStorage.getItem('dominio_id') || '';      // = ambito_rel_id
const categoria_id = localStorage.getItem('categoriaSeleccionadaId') || '';  // = categoria_rel_id
const codigo_postal_id = localStorage.getItem('codigoPostal') || '';

const publicacion_id = pubIdRaw === '' ? null : Number(pubIdRaw);
const raw = document.getElementById('waTelefonoInput').value.trim();

// Validación: +E.164
if (!/^\+\d{8,}$/.test(raw)) {
  alert('Ingresá el número en formato internacional, ej: +393445977100');
  return;
}
const isPrimary = document.getElementById('waIsPrimary').checked;

const payload = {
  user_id: Number(ownerId),
  publicacion_id,                 // null o número
  valor: raw,
  is_primary: isPrimary,
  // contexto opcional
  ambito_rel_id: dominio_id ? Number(dominio_id) : null,
  categoria_rel_id: categoria_id ? Number(categoria_id) : null,
  codigo_postal_id: codigo_postal_id 
};

  try {
    let res = await fetch('/social-chats-whatssapp/whatsapp/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin',
      cache: 'no-store',
      body: JSON.stringify(payload)
    });

    // 2) Si ya existe (409), buscamos y actualizamos (PUT) -> upsert
    if (res.status === 409) {
      // Traer el que corresponda a este scope
      const qs = new URLSearchParams({
        user_id: String(ownerId),
        ...(publicacion_id != null ? { publicacion_id: String(publicacion_id) } : {})
      }).toString();

      const listRes = await fetch(`/social-chats-whatssapp/whatsapp?${qs}`, {
        credentials: 'same-origin',
        cache: 'no-store'
      });
      if (!listRes.ok) throw new Error('No se pudo listar contactos existentes');

      const items = await listRes.json();
      if (!Array.isArray(items) || items.length === 0) throw new Error('No se encontró contacto a actualizar');

      // elegimos el primary si hay, si no el primero
      const target = items.find(i => i.is_primary) || items[0];

      res = await fetch(`/social-chats-whatssapp/whatsapp/${target.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        cache: 'no-store',
        body: JSON.stringify({ valor: raw, is_primary: true, is_active: true })
      });
      if (!res.ok) throw new Error('No se pudo actualizar el WhatsApp existente');
    } else if (!res.ok) {
      // cualquier otro error distinto de 201 y 409
      const txt = await res.text().catch(() => '');
      throw new Error(`Error HTTP ${res.status} ${txt}`);
    }
    
    // 3) LocalStorage (para uso inmediato del href)
    localStorage.setItem(`numTelefono:${ownerId}`, raw);

    // 4) Refrescar botón WhatsApp si existe
    const a = document.querySelector('.whatsapp-float');
    if (a) {
      const digits = raw.replace(/\D/g, ''); // wa.me solo dígitos
      const msg = `Hola, vi tu publicación: {{ post.titulo }} (ID {{ post.publicacion_id }}). Me interesa.`;
      a.href = `https://wa.me/${digits}?text=${encodeURIComponent(msg)}`;
      a.style.display = '';
    }

    // 5) Cerrar modal + feedback
    bootstrap.Modal.getInstance(document.getElementById('modalWhatsapp')).hide();
    alert('Número de WhatsApp guardado ✓');

  } catch (err) {
    console.error(err);
    alert('No se pudo guardar el número. Revisá la conexión o el formato.');
  }
}


document.addEventListener('DOMContentLoaded', () => {
  const btn     = document.getElementById('openChannelsModal');
  const modalEl = document.getElementById('modalWhatsapp');
  if (!btn || !modalEl) return;

  const modal = new bootstrap.Modal(modalEl);

  btn.addEventListener('click', () => {
    const userId = parseInt(localStorage.getItem('usuario_id') || '', 10);
    const tel = (Number.isInteger(userId) && userId > 0) ? getTelefonoCacheado(userId) : null;

    // Prefill visor + input + checkbox
    const visor = document.getElementById('waTelefonoActualText');
    const input = document.getElementById('waTelefonoInput');
    const chk   = document.getElementById('waIsPrimary');

    if (visor) visor.textContent = tel || '—';
    if (input) input.value = tel || '';
    if (chk)   chk.checked = !!tel;

    modal.show();
  });
});

function getTelefonoCacheado(userId) {
  return localStorage.getItem(`numTelefono:${userId}`) || null;
}