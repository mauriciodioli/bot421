(function () {
  const LS = window.localStorage;
  const hash = window.location.hash; // ej: "#60-001&es"
  if (!hash) return;

  const m = /^#([^&\/\s]+)&([a-z]{2})$/i.exec(hash);
  if (!m) return;

  const cp   = m[1];
  const lang = m[2].toLowerCase();

  // Validación mínima
  if (/^[0-9A-Za-z\-]{3,10}$/.test(cp)) {
    LS.setItem('codigoPostal', cp);
  }
  if (/^[a-z]{2}$/.test(lang)) {
    LS.setItem('language', lang);
    document.cookie = `language=${lang}; path=/; max-age=${3600*24*365}`;
  }

  // Limpia el hash para no re-procesar
  history.replaceState({}, '', window.location.pathname + window.location.search);
})();