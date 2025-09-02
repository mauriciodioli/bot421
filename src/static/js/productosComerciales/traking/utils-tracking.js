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


function observeCardImpression(pubId) {
  
  const card = document.getElementById(`card-${pubId}`);
  if (!card) return;
  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        trackImpressionOnce(pubId);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.5 });
  io.observe(card);
}

let lastClickTs = 0;
document.addEventListener('click', async (e) => {
  const a = e.target.closest('a[data-ali-redirect="1"]');
  if (!a) return;

  const now = Date.now();
  if (now - lastClickTs < 1200) { // anti-doble click
    e.preventDefault();
    return;
  }
  lastClickTs = now;
  e.preventDefault();

  const payload = {
    pub_id:   Number(a.dataset.pubId),
    vid:      String(a.dataset.vid || ''),
    user_id:  String(a.dataset.userId || ''),
    lang:     String(a.dataset.lang || 'es'),
  };

  try {
    const res = await fetch('/productosComerciales/traking/r/ali/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true,
      cache: 'no-store',
      credentials: 'same-origin',
      redirect: 'manual',    // ← para capturar Location en 302/3xx
    });

     if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    if (data && data.url) {
      window.location.assign(data.url);
      return;
    }
    // si no vino url, usá fallback
    if (fallback) window.location.assign(fallback);

  } catch (err) {
    if (fallback) window.location.assign(fallback);
  }
}, true);




                   