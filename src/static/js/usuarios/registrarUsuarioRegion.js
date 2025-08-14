document.addEventListener('DOMContentLoaded', cargarPaises);

const API_URL = 'https://restcountries.com/v3.1/all?fields=name,cca2,languages';

async function cargarPaises() {
  const selectPais = document.getElementById('pais');
  if (!selectPais) {
    console.error('No existe <select id="pais"> en el DOM.');
    return;
  }

  // Opción por defecto
  selectPais.innerHTML = '<option value="">--Seleccionar--</option>';
  window.paisesData = {};

  try {
    const response = await fetch(API_URL, { cache: 'no-store' });
    if (!response.ok) {
      const msg = await response.text().catch(() => '');
      throw new Error(`HTTP ${response.status} ${response.statusText} - ${msg.slice(0,120)}`);
    }

    const paises = await response.json();
    if (!Array.isArray(paises)) throw new Error('Formato inesperado: la respuesta no es un array.');

    paises
      .filter(p => p?.cca2 && p?.name?.common)
      .sort((a, b) => a.name.common.localeCompare(b.name.common))
      .forEach(pais => {
        const option = document.createElement('option');
        option.value = pais.cca2;
        option.textContent = pais.name.common;
        selectPais.appendChild(option);

        window.paisesData[pais.cca2] = {
          nombre: pais.name.common,
          idiomas: Object.values(pais.languages || {})
        };
      });
  } catch (error) {
    console.error('Error al cargar los países:', error);

    // Fallback mínimo para no bloquear el registro
    const fallback = [
      { code: 'PL', name: 'Poland',  languages: ['Polish'] },
      { code: 'IT', name: 'Italy',   languages: ['Italian'] },
      { code: 'ES', name: 'Spain',   languages: ['Spanish'] },
      { code: 'US', name: 'United States', languages: ['English'] },
    ];

    fallback.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.code;
      opt.textContent = p.name;
      selectPais.appendChild(opt);
      window.paisesData[p.code] = { nombre: p.name, idiomas: p.languages };
    });
  }
}

function seleccionarIdioma() {
  const paisSelect = document.getElementById('pais');
  const selectLenguaje = document.getElementById('lenguaje');
  if (!paisSelect || !selectLenguaje) return;

  const paisCodigo = paisSelect.value;
  const datosPais = (window.paisesData || {})[paisCodigo];

  // Reset de idiomas
  selectLenguaje.innerHTML = '<option value="">--Seleccionar--</option>';

  if (datosPais && Array.isArray(datosPais.idiomas) && datosPais.idiomas.length) {
    datosPais.idiomas.forEach(idioma => {
      const option = document.createElement('option');
      option.value = idioma;
      option.textContent = idioma;
      selectLenguaje.appendChild(option);
    });
  }

  // Actualizar etiquetas (si existen)
  const lblPais = document.querySelector('label[for="pais"]');
  const lblLang = document.querySelector('label[for="lenguaje"]');
  if (lblPais) lblPais.textContent = `País seleccionado: ${datosPais?.nombre || '—'}`;
  if (lblLang) lblLang.textContent = 'Selecciona tu idioma:';

  // Pasar a la siguiente sección
  mostrarSiguiente('seleccionPais', 'seleccionLenguaje');
}

function mostrarCodigoPostal() {
  const selectLenguaje = document.getElementById('lenguaje');
  if (selectLenguaje && selectLenguaje.value) {
    mostrarSiguiente('seleccionLenguaje', 'seleccionCodigoPostal');
    const cp = document.getElementById('codigoPostal');
    if (cp) cp.focus();
  }
}

function mostrarSiguiente(actual, siguiente) {
  const a = document.getElementById(actual);
  const s = document.getElementById(siguiente);
  if (a) a.style.display = 'none';
  if (s) s.style.display = 'block';
}

async function enviarDatos() {
  const pais = (document.getElementById('pais') || {}).value || '';
  const lenguaje = (document.getElementById('lenguaje') || {}).value || '';
  const codigoPostal = (document.getElementById('codigoPostal') || {}).value || '';
  const correo_electronico = (document.getElementById('correo_electronico') || {}).value || '';
  const password = (document.getElementById('password') || {}).value || '';

  // Validación mínima
  if (!pais || !lenguaje || !codigoPostal || !correo_electronico || !password) {
    alert('Completa país, idioma, código postal, correo y contraseña.');
    return;
  }

  const region = 'region';
  const provincia = 'provincia';
  const ciudad = 'ciudad';

  // Geolocalización tolerante a errores
  const ubic = await obtenerUbicacion().catch(() => ({}));
  const latitude = ubic?.latitude ?? null;
  const longitude = ubic?.longitude ?? null;

  const datos = {
    pais,
    lenguaje,
    codigoPostal,
    correo_electronico,
    password,
    region,
    provincia,
    ciudad,
    latitud: latitude,
    longitud: longitude
  };

  try {
    const response = await fetch('/registro-usuario/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    });

    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`Registro fallido: HTTP ${response.status} - ${text.slice(0,200)}`);
    }

    // Si el backend devuelve HTML, lo renderizamos.
    const html = await response.text();
    document.open();
    document.write(html);
    document.close();
  } catch (error) {
    console.error('Error al enviar los datos:', error);
    alert('No se pudo completar el registro. Intenta nuevamente.');
  }
}

function obtenerUbicacion() {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      return reject(new Error('Geolocalización no soportada por este navegador.'));
    }
    navigator.geolocation.getCurrentPosition(
      pos => resolve({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude
      }),
      err => reject(err),
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
    );
  });
}
