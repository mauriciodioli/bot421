// static/js/media/publicaciones/codigos_postales.js
document.addEventListener('DOMContentLoaded', () => {
  // Crear
  document.getElementById('form-crear-cp')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const payload = {
      codigoPostal: document.getElementById('cp-nuevo').value.trim(),
      ciudad: document.getElementById('cp-ciudad-nueva').value.trim(),
      pais: document.getElementById('cp-pais-nuevo').value.trim(),
    };
    if (!payload.codigoPostal) return alert('Código Postal requerido');
    const res = await fetch('/social-media-ambitos-codigosPostales-crear/', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (!res.ok || !json.ok) return alert(json.error || 'Error al crear');
    location.reload();
  });

  // Abrir modal editar
  const editarModal = document.getElementById('editarCodigoPostalModal');
  editarModal?.addEventListener('show.bs.modal', (event) => {
    const btn = event.relatedTarget;
    document.getElementById('cp-id-editar').value       = btn.getAttribute('data-cp-id');
    document.getElementById('cp-codigo-editar').value   = btn.getAttribute('data-codigo-postal') || '';
    document.getElementById('cp-ciudad-editar').value   = btn.getAttribute('data-ciudad') || '';
    document.getElementById('cp-pais-editar').value     = btn.getAttribute('data-pais') || '';
  });

  // Submit editar
  document.getElementById('form-editar-cp')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id  = document.getElementById('cp-id-editar').value;
    const payload = {
      codigoPostal: document.getElementById('cp-codigo-editar').value.trim(),
      ciudad: document.getElementById('cp-ciudad-editar').value.trim(),
      pais: document.getElementById('cp-pais-editar').value.trim(),
    };
    const res = await fetch(`/api/codigos-postales/${id}`, {
      method:'PUT', headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (!res.ok || !json.ok) return alert(json.error || 'Error al actualizar');
    location.reload();
  });

  // Abrir modal eliminar
  const eliminarModal = document.getElementById('eliminarCodigoPostalModal');
  let idAEliminar = null;
  eliminarModal?.addEventListener('show.bs.modal', (event) => {
    const btn = event.relatedTarget;
    idAEliminar = btn.getAttribute('data-cp-id');
    const codigo = btn.getAttribute('data-codigo-postal');
    document.getElementById('cp-codigo-eliminar').textContent = codigo || '';
  });

  // Confirmar eliminar
  document.getElementById('btn-confirmar-eliminar')?.addEventListener('click', async () => {
    if (!idAEliminar) return;
    const res = await fetch(`/api/codigos-postales/${idAEliminar}`, { method:'DELETE' });
    const json = await res.json();
    if (!res.ok || !json.ok) return alert(json.error || 'Error al eliminar');
    location.reload();
  });
});














(function() {
  // Helpers
  function ls(key) {
    return localStorage.getItem(key);
  }

  function renderRows(items) {
    const tbody = document.getElementById('acp-tbody');
    tbody.innerHTML = '';
    items.forEach(cp => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><input type="checkbox" class="acp-check" data-id="${cp.id}" data-cp="${cp.codigoPostal}"></td>
        <td>${cp.id}</td>
        <td>${cp.codigoPostal ?? ''}</td>
        <td>${cp.ciudad ?? ''}</td>
        <td>${cp.pais ?? ''}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function filtrarTabla() {
    const q = (document.getElementById('acp-buscar').value || '').toLowerCase();
    const rows = Array.from(document.querySelectorAll('#acp-tbody tr'));
    rows.forEach(tr => {
      const text = tr.innerText.toLowerCase();
      tr.style.display = text.includes(q) ? '' : 'none';
    });
  }

  // Abrir modal -> cargar lista (con POST)
document.getElementById('asignarCPAmbitoCategoriaModal')
  ?.addEventListener('show.bs.modal', function (ev) {
    const btn = ev.relatedTarget;
    const ambitoCategoriaId = btn?.getAttribute('data-ambitoCategoria-id') || '';
    const nombreCat = btn?.getAttribute('data-nombre') || '';

    document.getElementById('acp-ambitoCategoria-id').value = ambitoCategoriaId;
    document.getElementById('acp-nombre-cat').textContent = nombreCat;

    const pais   = localStorage.getItem('pais')    || localStorage.getItem('country')   || '';
    const idioma = localStorage.getItem('idioma')  || localStorage.getItem('lenguaje')  || localStorage.getItem('language') || '';

    document.getElementById('acp-filtro-pais').value   = pais;
    document.getElementById('acp-filtro-idioma').value = idioma;

    fetch('/social-media-ambitos-codigosPostales-listar/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pais, idioma }) // <- ahora POST con JSON
    })
    .then(r => {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return r.json();
    })
    .then(json => {
      const ok = json.ok !== false;
      const data = ok ? (json.data || json) : [];
      renderRows(data);
      document.getElementById('acp-alert').classList.toggle('d-none', (data || []).length > 0);
      document.getElementById('acp-guardar').disabled = true;
    })
    .catch(() => {
      renderRows([]);
      document.getElementById('acp-alert').classList.remove('d-none');
    });
  });


  // Check-all
  document.getElementById('acp-check-all')?.addEventListener('change', function() {
    document.querySelectorAll('.acp-check').forEach(ch => ch.checked = this.checked);
    document.getElementById('acp-guardar').disabled = !document.querySelector('.acp-check:checked');
  });

  // Habilitar guardar cuando marcan algo
  document.getElementById('acp-tbody')?.addEventListener('change', function(e) {
    if (e.target.classList.contains('acp-check')) {
      const any = document.querySelector('.acp-check:checked');
      document.getElementById('acp-guardar').disabled = !any;
      if (!e.target.checked) {
        document.getElementById('acp-check-all').checked = false;
      }
    }
  });

  // Buscar
  document.getElementById('acp-buscar')?.addEventListener('input', filtrarTabla);

  // (Opcional) Guardar asignaciones más adelante
          document.getElementById('acp-guardar')?.addEventListener('click', async function () {
          const ambitoCategoriaId = document.getElementById('acp-ambitoCategoria-id').value;
          const seleccionados = Array.from(document.querySelectorAll('.acp-check:checked'))
            .map(ch => Number(ch.getAttribute('data-id')));

          if (!seleccionados.length) return;

          try {
            const result = await asignarCPsACategoria(ambitoCategoriaId, seleccionados);
            console.log('Asignación OK:', result); // {ok:true, added, skipped}
            // acá podés refrescar chips/lista si querés
          } catch (err) {
            alert(err.message || 'No se pudo asignar los CP');
          }
        });

})();





// Llamada reusable para asignar CPs a una categoría (AmbitoCategoria)
async function asignarCPsACategoria(ambitoCategoriaId, codigoPostalIds, opts = {}) {
  const { closeOnSuccess = true } = opts;
  const btn = document.getElementById('acp-guardar');

  if (!ambitoCategoriaId) throw new Error('Falta ambitoCategoriaId');
  if (!Array.isArray(codigoPostalIds) || codigoPostalIds.length === 0) {
    throw new Error('Seleccioná al menos un CP');
  }

  try {
    btn?.setAttribute('disabled', 'disabled');

    const res = await fetch('/social-media-ambitos-codigosPostales-asignar-CP-categoria/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ambito_categoria_id: Number(ambitoCategoriaId),
        codigo_postal_ids: codigoPostalIds.map(Number)
      })
    });

    const json = await res.json();
    if (!res.ok || json.ok === false) {
      throw new Error(json.error || `Error HTTP ${res.status}`);
    }

    // opcional: cerrar modal al éxito
    if (closeOnSuccess) {
      const modalEl = document.getElementById('asignarCPAmbitoCategoriaModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal?.hide();
    }

    return json; // { ok:true, added, skipped }
  } finally {
    btn?.removeAttribute('disabled');
  }
}
















// -------- funciones reutilizables --------
function renderListaCP(items) {
  const tbody = document.getElementById('lcp-tbody');
  tbody.innerHTML = '';
  items.forEach(cp => {

    
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${cp.id}</td>
      <td>${cp.codigoPostal ?? ''}</td>
      <td>${cp.ciudad ?? ''}</td>
      <td>${cp.pais ?? ''}</td>
    `;
    tbody.appendChild(tr);
  });
}

function filtrarTablaLCP() {
  const q = (document.getElementById('lcp-buscar').value || '').toLowerCase();
  const rows = Array.from(document.querySelectorAll('#lcp-tbody tr'));
  rows.forEach(tr => {
    tr.style.display = tr.innerText.toLowerCase().includes(q) ? '' : 'none';
  });
}

async function fetchCPAsignadosDeCategoria(ambitoCategoriaId) {
  const res = await fetch('/social-media-ambitos-codigosPostales-listar-CP-de-categoria/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ambito_categoria_id: Number(ambitoCategoriaId) })
  });
  const json = await res.json();
  if (!res.ok || json.ok === false) {
    throw new Error(json.error || `Error HTTP ${res.status}`);
  }
  return json.data || [];
}

// -------- wiring del modal --------
document.getElementById('listaCPAmbitoCategoriaModal')
  ?.addEventListener('show.bs.modal', async function (ev) {
    const btn = ev.relatedTarget;
    const ambitoCategoriaId = btn?.getAttribute('data-ambitoCategoria-id') || '';
    const nombreCat = btn?.getAttribute('data-nombre') || '';

    document.getElementById('lcp-ambitoCategoria-id').value = ambitoCategoriaId;
    document.getElementById('lcp-nombre-cat').textContent = nombreCat;

    // limpiar y cargar
    document.getElementById('lcp-buscar').value = '';
    renderListaCP([]);
    document.getElementById('lcp-alert').classList.add('d-none');

    try {
      const data = await fetchCPAsignadosDeCategoria(ambitoCategoriaId);
      renderListaCP(data);
      document.getElementById('lcp-alert').classList.toggle('d-none', data.length > 0);
    } catch (e) {
      renderListaCP([]);
      document.getElementById('lcp-alert').classList.remove('d-none');
      console.error(e);
    }
  });

// filtro en vivo
document.getElementById('lcp-buscar')?.addEventListener('input', filtrarTablaLCP);






// POST para desasignar uno o varios CP de una categoría
async function desasignarCPsDeCategoria(ambitoCategoriaId, codigoPostalIds) {
  if (!ambitoCategoriaId) throw new Error('Falta ambitoCategoriaId');
  if (!Array.isArray(codigoPostalIds) || !codigoPostalIds.length) throw new Error('Sin CP a desasignar');

  const res = await fetch('/social-media-ambitos-codigosPostales-quitar-CP-categoria/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ambito_categoria_id: Number(ambitoCategoriaId),
      codigo_postal_ids: codigoPostalIds.map(Number)
    })
  });
  const json = await res.json();
  if (!res.ok || json.ok === false) {
    throw new Error(json.error || `Error HTTP ${res.status}`);
  }
  return json; // { ok:true, removed: N, not_found: M }
}

// Click en el botón 🗑️ de cada fila
document.getElementById('lcp-tbody')?.addEventListener('click', async (e) => {
  const btn = e.target.closest('.lcp-del');
  if (!btn) return;

  const cpId = Number(btn.getAttribute('data-id'));
  const catId = Number(document.getElementById('lcp-ambitoCategoria-id').value);

  btn.disabled = true;
  try {
    await desasignarCPsDeCategoria(catId, [cpId]);
    // sacar la fila de la tabla
    const tr = btn.closest('tr');
    tr?.parentNode?.removeChild(tr);
    // si quedó vacío, mostrar alerta
    if (!document.querySelector('#lcp-tbody tr')) {
      document.getElementById('lcp-alert').classList.remove('d-none');
    }
  } catch (err) {
    alert(err.message || 'No se pudo desasignar el CP');
    btn.disabled = false;
  }
});





function renderListaCP(items) {
  const tbody = document.getElementById('lcp-tbody');
  tbody.innerHTML = '';
  items.forEach(cp => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${cp.id}</td>
      <td>${cp.codigoPostal ?? ''}</td>
      <td>${cp.ciudad ?? ''}</td>
      <td>${cp.pais ?? ''}</td>
      <td>
        <button type="button" class="btn btn-sm btn-outline-danger lcp-del"
          data-id="${cp.id}" title="Quitar CP">🗑️</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}
