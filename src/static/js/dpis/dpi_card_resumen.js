(function(){
  const section = document.querySelector('section.s-numbers.dpia-resumen');
  if(!section) return;

  // Si está oculta (p. ej. mobile con display:none), no animar
  if(getComputedStyle(section).display === 'none') return;

  const spans = section.querySelectorAll('.s-numbers__value span');
  if(!spans.length) return;

  const animateTo = (el, target, keepPlus, duration = 1200) => {
    const start = 0;
    const t0 = performance.now();
    const tick = (now) => {
      const p = Math.min(1, (now - t0) / duration);
      const eased = 1 - Math.pow(1 - p, 3);   // easeOutCubic
      const val = Math.round(start + (target - start) * eased);
      el.textContent = keepPlus ? (val + '+') : String(val);
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  const parse = (txt) => {
    const raw = (txt || '').trim();
    return {
      keepPlus: /\+$/.test(raw),
      value: Number(raw.replace(/[^\d]/g, '')) || 0
    };
  };

  const startCounting = () => {
    spans.forEach((span) => {
      const { keepPlus, value } = parse(span.textContent);
      span.textContent = keepPlus ? '0+' : '0';
      animateTo(span, value, keepPlus);
    });
  };

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        startCounting();
        io.disconnect();
      }
    });
  }, { threshold: 0.2 });

  io.observe(section);
})();