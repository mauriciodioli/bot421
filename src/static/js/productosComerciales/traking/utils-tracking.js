// utils-tracking.js
function getVisitorId() {
  let vid = localStorage.getItem('visitor_id');
  if (!vid) {
    vid = crypto.randomUUID ? crypto.randomUUID() : String(Date.now()) + Math.random().toString(16).slice(2);
    localStorage.setItem('visitor_id', vid);
  }
  return vid;
}

function trackImpressionOnce(pubId) { 
  try {
    const user_id = localStorage.getItem('usuario_id') || '';
    const vid = getVisitorId() || '';
    const lang = window.currentLang || 'es';
    
    const payload = {
      pub_id: pubId,
      vid: vid,
      user_id: user_id,
      lang: lang,
    };

    const url = `/productosComerciales/traking/afiliado/impresion/`;
    const body = JSON.stringify(payload);

    // 1) Intentar con sendBeacon (POST JSON)
    let sent = false;
    if (navigator.sendBeacon) {
      const blob = new Blob([body], { type: 'application/json' });
      sent = navigator.sendBeacon(url, blob);
    }

    // 2) Fallback: POST con fetch
    if (!sent) {
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
        cache: 'no-store',
        credentials: 'same-origin',
      }).catch(() => {});
    }
  } catch { /* nada, fire-and-forget */ }
}










// === Captura POPUP: toma SIEMPRE el clic antes que utils-tracking ===
(function popupImpressionCapture() {
  let lastTs = 0;

  window.addEventListener('click', function (e) {
    // 1) ¿clic en la imagen del popup o en el botón?
    const popupA = e.target.closest('.dpia-popup a[href]');
    const btn    = e.target.closest('a.btn-afiliado-popup');
    if (!popupA && !btn) return;

    // 2) Buscar el href real del popup
    const spot = (popupA ? popupA.closest('.dpia-spot')
                         : (btn.closest('.dpia-spot') || btn.previousElementSibling));
    const refA = popupA || (spot && spot.querySelector('.dpia-popup a[href]'));
    const ref  = refA && refA.href;
    if (!ref) return;

      // === NUEVO: extraer alt y src del <img> dentro del anchor del popup ===
    const imgEl  = refA.querySelector('img');
    const altTxt = (imgEl && imgEl.getAttribute('alt') || '').trim();
    const imgSrc = (imgEl && imgEl.getAttribute('src') || '').trim();

    // 3) Anti doble clic
    const now = Date.now();
    if (now - lastTs < 700) { e.preventDefault(); e.stopPropagation(); return; }
    lastTs = now;

    // 4) Frenar propagación: QUE NO LO AGARRE utils-tracking (data-ali-redirect)
    e.preventDefault();
    e.stopPropagation();

    // 5) PubId desde el href (ej: .../748/layout)
    const m = ref.match(/\/(\d+)(?:\/|$)/);
    const pub_id = m ? Number(m[1]) : 0;

    // 6) Enviar impresión del POPUP (sendBeacon/keepalive)
    const payload = {
      pub_id,
      vid:  localStorage.getItem('visitor_id') || (typeof getVisitorId==='function' ? getVisitorId() : ''),
      user_id: localStorage.getItem('usuario_id') || '',
      lang: window.currentLang || localStorage.getItem('language') || 'es',
      afiliado_link: ref,

       // === NUEVO: pasar alt y src ===
      alt: altTxt,
      titulo: altTxt,          
      imagen_url: imgSrc,

      categoria_id:localStorage.getItem('categoriaSeleccionadaId'),
      ambito:this.localStorage.getItem('dominio')     
    };
    const body = JSON.stringify(payload);

    let sent = false;
    if (navigator.sendBeacon) {
      sent = navigator.sendBeacon('/productosComerciales/traking/afiliado/impresion_popup/',
              new Blob([body], { type: 'application/json' }));
    }
    if (!sent) {
      fetch('/productosComerciales/traking/afiliado/impresion_popup/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body,
        keepalive: true,
        cache: 'no-store',
        credentials: 'same-origin',
      }).catch(() => {});
    }

    // 7) Redirigir al href real del popup
    window.location.assign(ref);
  }, { capture: true, passive: false }); // << captura para ganarle a utils
})();
