
// ======================================================
// dpi.js — versión unificada (fix modal/foco) + dominios/categorías
// ======================================================
// Si alguien llama cargarAmbitos() directo, lo vemos en consola con stack:
(function wrapDirectCalls(){
  const _orig = window.cargarAmbitos;
  if (typeof _orig === 'function') {
    window.cargarAmbitos = function(){
      console.trace('[WARN] llamada directa a cargarAmbitos()');
      return _orig.apply(this, arguments);
    };
  }
})();
(function bootOnce () {
  if (window.__dpiBooted) return;
  window.__dpiBooted = true;

  // -----------------------------
  // Utils cookies (única definición)
  // -----------------------------
  function getCookie(name) {
    const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]+)'));
    return m ? decodeURIComponent(m[1]) : null;
  }
  function setCookie(name, value, maxAgeSeconds) {
    document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAgeSeconds}; SameSite=Lax`;
  }
function setCookieOverwrite(name, value, days = 365) {
  const maxAge = days * 24 * 60 * 60;

  // Borro posibles valores previos
  document.cookie = `${name}=; path=/; max-age=0; samesite=lax`;
  document.cookie = `${name}=; max-age=0; samesite=lax`; // por si lo guardaron sin path

  // Escribo el nuevo valor
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
}


  // ======================================================
  // 1) ADMIN — navegación (sin reemplazar body.innerHTML)
  // ======================================================
  function handleAdminClick(event) {
    event.preventDefault();
    const token = localStorage.getItem('access_token');
    if (!token) {
      alert('No se encontró un token de acceso.');
      return;
    }
    // Render del servidor completo:
    window.location.href = '/herramientaAdmin-administracion';
  }

  // ======================================================
  // 2) Links que envían formularios (ventas/compras/consultas)
  // ======================================================
  function wireFormLinks() {
    const ventas = document.getElementById('ventas-link');
    if (ventas) {
      ventas.addEventListener('click', function (e) {
        e.preventDefault();
        const form = document.getElementById('ventas-form');
        if (!form) return;
        const access_token = localStorage.getItem('access_token') || '';
        const ambito = localStorage.getItem('dominio') || '';
        const t = document.getElementById('access_token_form_Ventas');
        const a = document.getElementById('ambito_form_Ventas');
        if (t) t.value = access_token;
        if (a) a.value = ambito;
        form.submit();
      });
    }

    const compras = document.getElementById('compras-link');
    if (compras) {
      compras.addEventListener('click', function (e) {
        e.preventDefault();
        const form = document.getElementById('compras-form');
        if (!form) return;
        const access_token = localStorage.getItem('access_token') || '';
        const ambito = localStorage.getItem('dominio') || '';
        const t = document.getElementById('access_token_btn_compras');
        const a = document.getElementById('ambito_btn_compras');
        if (t) t.value = access_token;
        if (a) a.value = ambito;
        form.submit();
      });
    }

    const consultas = document.getElementById('consultas-link');
    if (consultas) {
      consultas.addEventListener('click', function (e) {
        e.preventDefault();
        const form = document.getElementById('consultas-form');
        if (!form) return;
        const access_token = localStorage.getItem('access_token') || '';
        const ambito = localStorage.getItem('dominio') || '';
        const t = document.getElementById('access_token_btn_consultas');
        const a = document.getElementById('ambito_btn_consultas');
        if (t) t.value = access_token;
        if (a) a.value = ambito;
        form.submit();
      });
    }
  }

  // ======================================================
  // 3) Idioma — persistencia + selector visual 
  // ======================================================
  (function ensureLanguage() {
    let currentLanguage = getCookie("language");
    if (!currentLanguage) {
      currentLanguage = 'in';
      setCookie("language", currentLanguage, 31536000); // 1 año
    }
    localStorage.setItem("language", currentLanguage);
  })();

  function initLanguageSelector() {
    const selector  = document.getElementById("languageSelector");
    if (!selector) return;

    const selected  = selector.querySelector(".selected-language");
    const dropdown  = selector.querySelector(".language-dropdown");
    if (!selected || !dropdown) {
      console.warn("[lang] Falta .selected-language o .language-dropdown");
      return;
    }

    const languages = {
      in: { name: "English",  code: "ENG", flag: "https://flagcdn.com/24x18/us.png" },
      pl: { name: "Poland",   code: "PL",  flag: "https://flagcdn.com/24x18/pl.png" },
      fr: { name: "Français", code: "FR",  flag: "https://flagcdn.com/24x18/fr.png" },
      es: { name: "Español",  code: "ES",  flag: "https://flagcdn.com/24x18/es.png" },
      de: { name: "Deutsch",  code: "DE",  flag: "https://flagcdn.com/24x18/de.png" },
      it: { name: "Italiano", code: "IT",  flag: "https://flagcdn.com/24x18/it.png" },
      pt: { name: "Português",code: "PT",  flag: "https://flagcdn.com/24x18/pt.png" }
    };

    function buildDropdownOnce() {
      if (dropdown.dataset.built === "1") return;
      dropdown.innerHTML = "";
      for (const [code, lang] of Object.entries(languages)) {
        const opt = document.createElement("div");
        opt.className = "language-option";
        opt.innerHTML = `<img src="${lang.flag}" alt=""> ${lang.name}`;
        opt.addEventListener("click", (e) => {
          e.stopPropagation();
          setLanguage(code);
          closeMenu();
        });
        dropdown.appendChild(opt);
      }
      dropdown.dataset.built = "1";
    }

    function applyUI(lang) {
      const d = languages[lang];
      if (!d) return;
      selected.innerHTML = `<img src="${d.flag}" alt=""> ${d.code}`;
    }

    function setLanguage(lang) {
      if (!languages[lang]) return;
      localStorage.setItem("language", lang);
      setCookie("language", lang, 31536000); // 1 año
      applyUI(lang);

    
      triggerAmbitosReload('lang');


    }

    function openMenu() {
      buildDropdownOnce();
      selector.classList.add("is-open");
      dropdown.style.position = "absolute";
      dropdown.style.zIndex = "1050";
      dropdown.style.display = "block";
    }
    function closeMenu() {
      selector.classList.remove("is-open");
      dropdown.style.display = "none";
    }
    function toggleMenu() {
      if (selector.classList.contains("is-open")) closeMenu();
      else openMenu();
    }

    selector.addEventListener("click", function (e) {
      e.stopPropagation();
      toggleMenu();
    });

    document.addEventListener("click", function (e) {
      if (!selector.contains(e.target)) closeMenu();
    });

    const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
    applyUI(currentLang);
    buildDropdownOnce();
   

  }

  // ======================================================
  // 4) Código Postal — label + modal con fix de foco (ARIA)
  // ======================================================
  function cargaCodigoPostalLayout() {
    const labelCP = document.getElementById("labelCP");
    const cpValue = localStorage.getItem("codigoPostal") || "";
    if (labelCP) labelCP.textContent = cpValue;
  }

  function initCodigoPostalModal() {
    cargaCodigoPostalLayout();

    const modalEl  = document.getElementById('modalSeleccionCodigoPostal');
    const openLink = document.getElementById('openModalCP');
    if (!modalEl || !openLink) return;

    const modal   = bootstrap.Modal.getOrCreateInstance(modalEl);
    let lastFocus = null;

    function moveFocusOut() {
      const fallback = openLink || document.body;
      const active   = document.activeElement;
      if (modalEl.contains(active)) active.blur();
      if (fallback && typeof fallback.focus === 'function') {
        fallback.focus({ preventScroll: true });
      }
    }

    // Abrir modal
    openLink.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation();

      // Limpieza por si quedó algo de un modal previo
      document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
      document.body.classList.remove('modal-open');
      document.body.style.removeProperty('overflow');
      document.body.style.removeProperty('paddingRight');

      // Cerrar navbar colapsable si está abierta
      const nav = document.getElementById('navbarNav');
      if (nav && nav.classList.contains('show')) {
        const collapse = bootstrap.Collapse.getOrCreateInstance(nav);
        collapse.hide();
      }

      lastFocus = document.activeElement;

      // Pre-cargar input con lo guardado
      const input = document.getElementById('codigoPostalModal');
      if (input) input.value = localStorage.getItem('codigoPostal') || '';

      modal.show();
    });

    // Focus dentro al mostrar
    modalEl.addEventListener('shown.bs.modal', () => {
      const input = document.getElementById('codigoPostalModal');
      if (input) input.focus();
      modalEl.removeAttribute('aria-hidden');
    });

    // Mover foco fuera al empezar a cerrar (evita warning ARIA)
    modalEl.addEventListener('hide.bs.modal', () => {
      moveFocusOut();
    });

    // Devolver foco y limpieza dura al terminar de cerrar
    modalEl.addEventListener('hidden.bs.modal', () => {
      if (lastFocus && typeof lastFocus.focus === 'function') {
        lastFocus.focus({ preventScroll: true });
      }
      hardCloseModal(modalEl); // asegura que no quede backdrop ni body.modal-open
    });

    // Guardar CP y cerrar
    window.guardarCodigoPostal = function guardarCodigoPostal() {
      const input = document.getElementById('codigoPostalModal');
      const codigoPostal = (input?.value ?? '').trim();

      localStorage.setItem('codigoPostal', codigoPostal);
      setCookie('codigoPostal', codigoPostal, 3600); // 1 hora
      console.log("Código Postal guardado:", codigoPostal);

      cargaCodigoPostalLayout();

      // 👉 Disparar dominios y categorías (igual que en tu código “nuevo”)
      triggerAmbitosReload('cp');



      // Cerrar modal con limpieza y foco
      moveFocusOut();
      hardCloseModal(modalEl);
  

    };
  }

  // ======================================================
  // 5) (Opcional) Debug mínimo navbar/CP
  // ======================================================
  function wireDebug() {
    const navbarToggler = document.querySelector(".navbar-toggler");
    if (navbarToggler) {
      navbarToggler.addEventListener("click", function () {
        console.log("👉 Navbar toggler clickeado. aria-expanded:", navbarToggler.getAttribute("aria-expanded"));
        
   
      
      });
    }
    const cpLink = document.getElementById("openModalCP");
    if (cpLink) {
      cpLink.addEventListener("click", function () {
        console.log("👉 Click en CP");
       
      });
    }
  }

  // ======================================================
  // 6) DOMContentLoaded — enganchar todo una sola vez
  //    + carga inicial de dominios/categorías
  // ======================================================
  document.addEventListener('DOMContentLoaded', function () {
    const adminLink = document.getElementById('admin-link');
    if (adminLink) adminLink.addEventListener('click', handleAdminClick);

    wireFormLinks();
    initLanguageSelector();
    initCodigoPostalModal();
    wireDebug();

     triggerAmbitosReload('init');   // ✅ solo 1

  });

})(); // bootOnce IIFE

// ======================================================
// Limpieza defensiva de modal/backdrop
// ======================================================
function hardCloseModal(modalEl) {
  try {
    const inst = bootstrap.Modal.getInstance(modalEl) || bootstrap.Modal.getOrCreateInstance(modalEl);
    inst.hide();
  } catch (e) { /* noop */ }

  // Limpieza defensiva (por si quedó algo colgado)
  setTimeout(() => {
    document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    modalEl.classList.remove('show');
    modalEl.setAttribute('aria-hidden', 'true');
    modalEl.style.display = 'none';
    document.body.classList.remove('modal-open');
    document.body.style.removeProperty('overflow');
    document.body.style.removeProperty('paddingRight');
  }, 50);
}

function rebindDomainsUI() {
  const root = document.getElementById('domains');
  if (!root) return;

  const nav        = root.querySelector('#dx-nav');
  const pillsWrap  = root.querySelector('#dx-other-pills');
  const activePill = root.querySelector('#dx-active-pill');

  function handleClick(e) {
    const btn = e.target.closest('button[data-id]');
    if (!btn) return;

    const id     = Number(btn.dataset.id);
    const nombre = btn.dataset.key || (btn.querySelector('.card-number')?.textContent?.trim() || '');

    // Persistir (LS)
    localStorage.setItem('dominio', nombre);
    localStorage.setItem('dominio_id', String(id));
debugger;
    // ✅ Pisar cookies existentes
    setCookieOverwrite('dominio', nombre);
    setCookieOverwrite('dominioValor', nombre);
    setCookieOverwrite('dominio_id', String(id));

    // UI
    if (activePill) activePill.textContent = nombre;
    if (nav) nav.querySelectorAll('button').forEach(b => b.classList.toggle('is-active', b === btn));
  }

  if (nav && !nav.dataset.bound) {
    nav.addEventListener('click', handleClick);
    nav.dataset.bound = '1';
  }
  if (pillsWrap && !pillsWrap.dataset.bound) {
    pillsWrap.addEventListener('click', handleClick);
    pillsWrap.dataset.bound = '1';
  }
}








// Debounce global para recargar DOMAINS una sola vez
let _domainsReloadTimer = null;
// Logger opcional
function logAmbitos(msg){ console.log(`[ambitos] ${msg}`); }


// SIEMPRE llamá a esto (NO llames cargarAmbitos() directo)
function triggerAmbitosReload(reason, delayMs = 120) {

  clearTimeout(_domainsReloadTimer);
  _domainsReloadTimer = setTimeout(() => {
    if (typeof cargarAmbitos === 'function') cargarAmbitos();
    if (typeof cargarAmbitosCarrusel === 'function') cargarAmbitosCarrusel();
  }, delayMs);
}


