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
  const user_id = localStorage.getItem('usuario_id');
  const vid = getVisitorId();
  const lang = encodeURIComponent(window.currentLang || 'es');
  const url = `/productosComerciales/traking/afiliado/impresion/` +
              `?pub_id=${pubId}` +
              `&vid=${encodeURIComponent(vid)}` +
              `&user_id=${encodeURIComponent(user_id)}` +
              `&lang=${lang}`;
  if (!navigator.sendBeacon || !navigator.sendBeacon(url)) {
    fetch(url, { method: 'POST' }).catch(()=>{});
  }
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
document.addEventListener('click', (e) => {
  const a = e.target.closest('a[data-ali-redirect="1"]');
  if (!a) return;
  const now = Date.now();
  if (now - lastClickTs < 1200) {
    e.preventDefault(); // evita doble click compulsivo
    return;
  }
  lastClickTs = now;
}, true);




                   