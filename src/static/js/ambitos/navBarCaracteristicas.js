let categoriasCache = {};


// === Esperar a que embed.js esté listo (robusto) ===
window.ensureEmbedReady = window.ensureEmbedReady || function () {
  return new Promise((resolve) => {
    
    if (typeof window.initEmbedPopups === 'function') return resolve();
    const t0 = Date.now();
    (function check () {
      if (typeof window.initEmbedPopups === 'function') return resolve();
      // evita loops infinitos: 10s timeout
      if (Date.now() - t0 > 10000) { console.warn('embed.js no apareció'); return resolve(); }
      setTimeout(check, 50);
    })();
  });
};





document.addEventListener('DOMContentLoaded', function () {
    // Seleccionamos el primer ítem que tiene el atributo 'data-color'
    const firstItem = document.querySelector('.categoria-dropdown-item[data-color]');

    // Si hay un primer ítem, actualizamos el color
    if (firstItem) {
        updateColor(firstItem);
    }

    // Aseguramos que la lógica solo se ejecute una vez para el primer ítem
    // Esto solo se ejecutará una vez en el evento 'DOMContentLoaded'
});


function updateColor(element) {
   
  
    if (!element) return; // Evita errores si no se pasa un elemento
    
    // Obtener el id del elemento
    let id = element.id;
    let colorElementCategoria = element.getAttribute('data-color');
    //console.log('ID obtenido:', id);
   

    let navTabs = document.querySelector('.nav-tabs');
    let homeTab = document.querySelector('#home-tab'); // Selecciona el botón "Home"

    // Elimina cualquier clase de color existente en la barra y en el botón "Home"
    navTabs.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');
    homeTab.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');

    // Agrega la nueva clase de color para los elementos de la barra
    navTabs.classList.add('border-' + colorElementCategoria);
    homeTab.classList.add('border-' + colorElementCategoria);
}








// 1) Click en el "pill" activo => cargar categorías
$(document)
  .off('click.dpia', '#dx-active-pill')
  .on('click.dpia', '#dx-active-pill', function (e) {
    e.preventDefault();
    debugger;
    cargarAmbitosCategorias();
  });

// 2) Accesibilidad: Enter/Espacio también disparan la carga
$(document)
  .off('keydown.dpia', '#dx-active-pill')
  .on('keydown.dpia', '#dx-active-pill', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      cargarAmbitosCategorias();
      cargarCategoriasEnPills();
    }
  });

// 3) (Opcional) Marcarlo como botón y cursor “mano” una vez esté en el DOM
const activarPillComoBoton = () => {
  const pill = document.getElementById('dx-active-pill');
  if (pill) {
    pill.setAttribute('role', 'button');
    pill.setAttribute('tabindex', '0');
    pill.style.cursor = 'pointer';
  }
};
document.addEventListener('DOMContentLoaded', activarPillComoBoton);
// Si lo insertás más tarde, llamá activarPillComoBoton() después de inyectar `explore`.



// === 1) Hook: clic/tecla en el pill activo => cargar categorías en #dx-other-pills
$(document)
  .off('click.dpia', '#dx-active-pill')
  .on('click.dpia', '#dx-active-pill', function (e) {
    e.preventDefault();
    cargarCategoriasEnPills();
  });

$(document)
  .off('keydown.dpia', '#dx-active-pill')
  .on('keydown.dpia', '#dx-active-pill', function (e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      cargarCategoriasEnPills();
    }
  });

// Opcional: marcarlo como botón accesible
(function activarPillComoBoton(){
  const pill = document.getElementById('dx-active-pill');
  if (pill) {
    pill.setAttribute('role', 'button');
    pill.setAttribute('tabindex', '0');
    pill.style.cursor = 'pointer';
  }
})();

// === 2) Nueva función: carga categorías y las pinta en #dx-other-pills (borrando los dominios)
async function cargarCategoriasEnPills() {
  const $pills = $('#dx-other-pills');     // destino
  if (!$pills.length) {
    console.warn('#dx-other-pills no existe');
    return;
  }

  // Limpio y muestro estado "cargando"
  $pills.empty().append(`
    <div class="dpia-state" id="dx-cat-loading" style="padding:8px;opacity:.8">
      Cargando categorías…
    </div>
  `);

  // --- Payload (igual a tu lógica)
  let ambito = localStorage.getItem('dominio');
  const cpRaw = localStorage.getItem('codigoPostal');
  if (ambito === 'inicialDominio') ambito = 'Laboral';

  const formData = new FormData();
  if (ambito != null && ambito !== 'null' && ambito !== '') formData.append('ambito', ambito);
  if (cpRaw  != null && cpRaw  !== 'null' && cpRaw  !== '') formData.append('cp', cpRaw);

  try {
    const res = await fetch('/social-media-ambitosCategorias-categoria-mostrar/', {
      method: 'POST',
      body: formData,
      headers: { 'Accept': 'application/json' }
    });

    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      console.error(`HTTP ${res.status}`, txt);
      return pintarEstado('Error al cargar categorías');
    }

    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      console.warn('La respuesta no es JSON.');
      return pintarEstado('Formato de respuesta inválido');
    }

    const data = await res.json();
    const categorias = Array.isArray(data?.categorias)
      ? data.categorias
      : Array.isArray(data?.data?.categorias)
      ? data.data.categorias
      : [];

    // Borro dominios y pinto categorías
    $pills.empty();

    if (!categorias.length) {
      return pintarEstado('Sin categorías disponibles');
    }

    // Render de cada categoría como "pill" (mismo look&feel)
    const frag = document.createDocumentFragment();

    categorias.forEach((categoria, index) => {
      const id     = categoria?.id ?? `cat-${index}`;
      const valor  = categoria?.valor ?? '';
      const nombre = categoria?.nombre ?? categoria?.name ?? `Categoría ${index + 1}`;
      const color  = categoria?.color || '#0b2033';

      const btn = document.createElement('button');
      btn.className = 'pill cat-pill';
      btn.setAttribute('data-id', id);
      btn.setAttribute('data-key', valor);
      // Reutilizo tu bg genérico; podés variar por categoría si querés
      btn.style.setProperty('--card-bg', "url('/static/img/images_dpi_tarjetas2.jpg')");

      btn.innerHTML = `
        <span class="card-number"  style="color:${color}">${nombre}</span>
        <input type="hidden" class="categoria-id-oculta" value="${id}">
      `;

      frag.appendChild(btn);
    });

    $pills[0].appendChild(frag);

  } catch (err) {
    console.error('Error de red/parseo al cargar categorías:', err);
    return pintarEstado('Error de red o parseo');
  }

  // Mensaje de estado en el mismo contenedor de pills
  function pintarEstado(texto) {
    $pills
      .empty()
      .append(`<div class="dpia-state" style="padding:8px;opacity:.8">${texto}</div>`);
  }
}

// === 3) (Opcional) Qué pasa cuando clickeo una categoría renderizada
//     - Guardamos selección y (si querés) navegar o refrescar publicaciones
$(document)
  .off('click.dpia', '.cat-pill')
  .on('click.dpia', '.cat-pill', function (e) {
    e.preventDefault();
    const $btn = $(this);
    const catId = $btn.data('id');
    const catKey = $btn.data('key') || '';

    // Visual: marcar activa
    $('.cat-pill').removeClass('is-active');
    $btn.addClass('is-active');

    // Guardar selección para otros módulos
     localStorage.setItem('categoria', String(catId));
    localStorage.setItem('categoriaSeleccionadaId', String(catId));
    localStorage.setItem('categoriaSeleccionadaKey', String(catKey));

    // TODO: acá dispará lo que corresponda en tu app:
     
// Realizar la solicitud AJAX al cargar la página

    var storedDomain = localStorage.getItem('dominio');
    let domain
    if (storedDomain && storedDomain !== 'null') {
        domain = storedDomain;
    } else {
      
        let currentURL = window.location.href;
        let partAfterIndex = currentURL.split("index/")[1];
        // Si la parte después de "index/" es undefined o vacía, asigna 'laboral'
        if (typeof partAfterIndex === 'undefined' || partAfterIndex === '') {
            partAfterIndex = 'Laboral';
        }
        console.log(partAfterIndex); // Mostrará "personal"
        domain = partAfterIndex;
        localStorage.setItem('dominio', domain); // Guarda 'personal' en el almacenamiento local con la clave 'dominio'
    }
    console.log('Dominio seleccionado:', domain, 'ID:', catId);
    
       if (document.querySelector('#navBarCaracteristicas-home')) {
        console.log("Ejecutando en home.html");
        cargarPublicaciones(domain,catId);
        // Después de cargar publicaciones o actualizar el texto
        const catKey = localStorage.getItem('categoriaSeleccionadaKey') || 'Categoría';
        $('#ambitoActualHome').text(catKey);

        // Scroll + foco en el H1
        scrollAndFocusElement('#ambitoActualHome', 100);
    }else{
        console.log("Ejecutando en index.html");
        enviarDominioAJAXDesdeCategorias(domain,catId);
         scrollAndFocusSection('domains-publicaciones', '#ambitoActual', /*offset navbar*/ 100);
      // (Opcional) actualizar el H1 con el texto de la categoría
          const $ambitoH1 = $('#ambitoActual');
          if ($ambitoH1.length && catKey) {
            $ambitoH1.text(catKey);
          }
    }

      // 👉 Scroll & focus a la sección de publicaciones
    //   - hace focus en el H1 #ambitoActual (si está)
   

  });


$(document).on('click', 'button[id^="card-"]', function () {
  console.log("Click en tarjeta:", this.id);

  // Siempre mueve el scroll hacia la pastilla activa
  scrollAndFocusElement('#dx-active-pill', 100);
   const dom = decodeURIComponent((document.cookie.split('; ').find(r=>r.startsWith('dominio='))||'').split('=')[1]||'');
   if (dom) {
    const a = document.querySelector('#ambito_actual a');
    if (a) a.textContent = dom;
  
  }
 

});

// === Helper: scroll suave hasta un elemento y darle foco ===
function scrollAndFocusElement(selector, offsetPx = 100) {
  const el = document.querySelector(selector);
  if (!el) {
    console.warn(`Elemento no encontrado: ${selector}`);
    return;
  }

  // Asegurar que sea focuseable
  if (!el.hasAttribute('tabindex')) {
    el.setAttribute('tabindex', '-1');
  }

  // Calcular coordenada con compensación de navbar
  const y = el.getBoundingClientRect().top + window.pageYOffset - offsetPx;

  // Hacer scroll suave
  window.scrollTo({ top: y, behavior: 'smooth' });

  // Dar foco después de un pequeño delay
  setTimeout(() => el.focus(), 400);
}


// Helper: scroll suave con compensación de navbar fija y focus accesible
function scrollAndFocusSection(targetId, focusSelector = null, offsetPx = 100) {
  debugger;
  const section = document.getElementById(targetId);
  if (!section) return;

  // Evita saltos: focus sin scroll primero
  section.setAttribute('tabindex', '-1'); // focusable para lectores de pantalla
  if (focusSelector) {
    const focusEl = section.querySelector(focusSelector) || section;
    focusEl.setAttribute('tabindex', focusEl.getAttribute('tabindex') || '-1');
    focusEl.focus({ preventScroll: true });
  } else {
    section.focus({ preventScroll: true });
  }

  // Scroll con offset (navbar fija)
  const y = section.getBoundingClientRect().top + window.pageYOffset - offsetPx;
  window.scrollTo({ top: y, behavior: 'smooth' });
}
































// Agregar un manejador de eventos de clic al botón
$('#caracteristicas-tab').on('click', function() {
    
    // Llamar a la función para cargar los ámbitos
    banderaCategorias = localStorage.getItem('banderaCategorias');
    if (banderaCategorias == 'True') {
        cargarAmbitosCategorias();   
        localStorage.setItem('banderaCategorias', 'False');
    }  
});




const dropdownMenuCategorias = $('.categoria-dropdown-menu');
dropdownMenuCategorias.empty();
// Función para cargar los ámbitos desde el servidor
async function cargarAmbitosCategorias() {
  // 1) Referencia al menú; si no está, salimos sin romper nada
  const dropdownMenuCategorias = $('#caracteristicas-tab').siblings('.categoria-dropdown-menu');
  if (!dropdownMenuCategorias.length) {
    console.warn("dropdownMenuCategorias no encontrado");
    return;
  }

  // 2) Armar payload con FormData (lo que ya usas)
  let ambito = localStorage.getItem('dominio');
  const cpRaw = localStorage.getItem('codigoPostal');

  if (ambito === 'inicialDominio') ambito = 'Laboral';

  const formData = new FormData();
  if (ambito != null && ambito !== 'null' && ambito !== '') formData.append('ambito', ambito);
  if (cpRaw != null && cpRaw !== 'null' && cpRaw !== '') formData.append('cp', cpRaw);
 
  try {
    // 3) Fetch (sin slash final para evitar 404/308, salvo que tu Flask lo pida)
    const res = await fetch('/social-media-ambitosCategorias-categoria-mostrar/', {
      method: 'POST',
      body: formData,
      headers: {
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      const txt = await res.text().catch(() => '');
      console.error(`HTTP ${res.status}`, txt);
      pintarEstado("Error al cargar categorías");
      return;
    }

    // 4) Confirmar que es JSON
    const ct = res.headers.get('content-type') || '';
    if (!ct.includes('application/json')) {
      console.warn('La respuesta no es JSON.');
      pintarEstado("Formato de respuesta inválido");
      return;
    }

    const data = await res.json();

    // 5) Normalizar estructura: admite data.categorias o data.data.categorias
    const categorias = Array.isArray(data?.categorias)
      ? data.categorias
      : Array.isArray(data?.data?.categorias)
      ? data.data.categorias
      : [];

    // 6) Render seguro
    dropdownMenuCategorias.empty();

    if (!categorias.length) {
      pintarEstado("Sin categorías disponibles");
      return;
    }

    categorias.forEach((categoria, index) => {
      const id = categoria?.id ?? `cat-${index}`;
      const valor = categoria?.valor ?? '';
      const nombre = categoria?.nombre ?? categoria?.name ?? `Categoría ${index + 1}`;
      const color = categoria?.color || 'orange';

      const itemHtml = `
        <li style="padding: 10px;">
          <a href="#" class="categoria-dropdown-item"
             id="${id}" data-value="${valor}" data-color="${color}"
             style="color:${color}; padding:10px;">
            ${nombre}
          </a>
        </li>
        <li class="cat-divider"><hr class="dropdown-divider"></li>
      `;
      dropdownMenuCategorias.append(itemHtml);
    });

    // 7) Quitar el último separador si existe
    dropdownMenuCategorias.find('li.cat-divider').last().remove();

    // 8) (Opcional) Delegar click para cerrar/actuar
    dropdownMenuCategorias.off('click', '.categoria-dropdown-item').on('click', '.categoria-dropdown-item', function (e) {
      e.preventDefault();
      const id = $(this).attr('id');
      // tu lógica al seleccionar categoría…
      dropdownMenuCategorias.closest('.dropdown').removeClass('show'); // si usas Bootstrap 5
    });

  } catch (err) {
    console.error('Error de red/parseo al cargar categorías:', err);
    pintarEstado("Error de red o parseo");
  }

  function pintarEstado(texto) {
    dropdownMenuCategorias
      .empty()
      .append(`<li><span class="dropdown-item disabled">${texto}</span></li>`);
  }
}






// Asegurar que al hacer clic en el botón de categoría, se vuelva a mostrar
$('.categoria-dropdown-toggle').on('click', function (e) {
    e.stopPropagation(); // Evita que el evento se propague y lo cierre inmediatamente
    $('.categoria-dropdown-menu').toggleClass('show'); // Alterna visibilidad
});


$('.categoria-dropdown-menu').removeClass('show');
// 1) EXTRAEMOS TU MISMO CÓDIGO A UNA FUNCIÓN (misma lógica, mismo this)
function onCategoriaClick(e) {
    e.preventDefault(); // Previene el comportamiento predeterminado
    
    let categoriaId = $(this).attr('id');
    let categoriaNombre = $(this).data('value');
    
    console.log("Categoría seleccionada:", categoriaNombre);
    console.log("Clic detectado"); // Para verificar si el clic está siendo detectado

    // Cerrar el menú desplegable correctamente
    $('.categoria-dropdown-menu').removeClass('show'); // Alternativa sin Bootstrap
    // $('.categoria-dropdown-toggle').dropdown('hide');  // Si usas Bootstrap

    const selectedCategory = this.id; // Obtiene el valor de data-value

    // Guardar el dominio en localStorage
    localStorage.setItem('categoria', selectedCategory);
    var domain = localStorage.getItem('dominio');

    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }

    $('#home-tab').text(this.dataset.value);  // Cambiar el texto del botón

    console.log('Dominio enviado desde categorias---------------:', domain);
    console.log('Categorias---------------:', selectedCategory);
    
    // Llamar a la función para manejar el dominio seleccionado
    if (document.querySelector('#navBarCaracteristicas-home')) {
        console.log("Ejecutando en home.html");
        cargarPublicaciones(domain, 'layout');
    }
    if (document.querySelector('#navBarCaracteristicas-index')) {
        console.log("Ejecutando en index.html");
        enviarDominioAJAXDesdeCategorias(domain, selectedCategory);
    }

    // Marcar el ítem como activo
    $('.categoria-dropdown-item').removeClass('active');
    $(this).addClass('active');

    updateColor($(this)[0]); // Convierte jQuery a elemento DOM puro
}

// 2) TU DELEGACIÓN JQUERY ORIGINAL (idéntica)
$(document).on('click', '.categoria-dropdown-item', function (e) {
    if (e._catDone) return;   // evita doble ejecución si llega por ambos caminos
    e._catDone = true;
    onCategoriaClick.call(this, e); // mantiene el mismo `this` y comportamiento
});

// 3) FALLBACK EN CAPTURA (NO CAMBIA LA LÓGICA: SOLO INVOCAMOS LA MISMA FUNCIÓN)
document.addEventListener('click', function (e) {
    const el = e.target.closest('.categoria-dropdown-item');
    if (!el) return;
    if (e._catDone) return;   // si ya lo manejó jQuery, no repetir
    e._catDone = true;
    onCategoriaClick.call(el, e); // mismo código, mismo `this`
}, true); // <- captura para esquivar stopPropagation ajeno













// Delegación de eventos para manejar clics en las tarjetas
$('.card-container').on('click', '.card', function () {
   // const selectedCategory = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();
     const selectedCategory = '1'; // Usar un valor fijo para pruebas
    // Guardar el dominio en localStorage
    localStorage.setItem('dominioValor', selectedCategory);
    var domain = localStorage.getItem('dominio');
    // Guardar también en cookie (expira en 30 días)
    document.cookie = `dominioValor=${encodeURIComponent(domain)}; path=/; max-age=${60 * 60 * 24 * 30}`;

    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }
    console.log('hiddenInput:', hiddenInput.val());
    // Mostrar en consola
    console.log('Categoria Valor seleccionada---------------:', selectedCategory);
    
     if (document.querySelector('#navBarCaracteristicas-home')) {
        console.log("Ejecutando en home.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
    }else{
        console.log("Ejecutando en index.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
    } 
    if (document.querySelector('#navBarCaracteristicas-mostrarGaleria')) {
        console.log("Ejecutando en mostrarGaleria.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
   
    }

    // Marcar la tarjeta como activa
    $('.card').removeClass('active');
    $(this).addClass('active');

    // Enfocar la sección
    $('.dpi-muestra-publicaciones-centrales')[0].focus();
});

// Llamar a la función para cargar los ámbitos al cargar la página
cargarAmbitosCategorias();




  


























function enviarDominioAJAXDesdeCategorias(domain,selectedCategory) { 
     // Bloqueo de duplicación
    //if (sessionStorage.getItem('dominioCategoriaCargado')) {
      //  console.log("enviarDominioAJAXDesdeCategorias ya ejecutado, se evita la duplicación.");
       // return;
   // }
   
    sessionStorage.setItem('dominioCategoriaCargado', 'true');   
    // Elementos relevantes
    const splash = document.querySelector('.splashCarga');
    const targetSection = document.querySelector('.dpi-muestra-publicaciones-centrales'); // Asegúrate de que esta clase esté bien definida
    cp = localStorage.getItem('codigoPostal');
        if (!cp){
            cp = '1';
        }

    if (!splash || !targetSection) {
        console.error("No se encontró el elemento 'splashCarga' o la sección 'domains'.");
        return;
    }

    // Mostrar/ocultar splash según la visibilidad de la sección
    toggleSplash(targetSection, splash);
  
    // Ruta al archivo con la galería de imágenes   
    var galeriaURL = '/media-publicaciones-mostrar-dpi/';
    var access_token = 'access_dpi_token_usuario_anonimo';
   
    if ( !localStorage.getItem('dominio')) {        
        localStorage.setItem('dominio', 'inicialDominio');
       
    }

   


   
    // Esperar a que se actualice el idioma en localStorage antes de continuar
    setTimeout(() => {
        
                let lenguaje = localStorage.getItem('language'); // Por defecto 'es' si no está definido


                $.ajax({
                type: 'POST',
                url: galeriaURL,
                dataType: 'json', // Asegúrate de que el backend devuelva un JSON
                headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
                data: { ambitos: domain,
                        categoria: selectedCategory,
                        codigoPostal: cp,   
                        lenguaje: lenguaje}, // Enviar el dominio como parte de los datos
                success: function (response) {
                // console.log('Respuesta del servidor:', response[0].ambito);
                  
                 
                    splash.style.display = 'none'; // Ocultar el splash al terminar
                    if (Array.isArray(response)) {
                        var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                        postDisplayContainer.empty();





                        let publicacionesValidas = 0;
                        // === Intercalado: config + anchor HTML (antes del forEach) ===
                        const popupCada = 1; // cada cuántas cards reales metés un popup
                        let cardsRenderizadas = 0;

                        const paramsPopup = {
                        dominio:  'Technologia',
                        categoria:'wearables',
                        lang:     'pl',
                        cp:       localStorage.getItem('codigoPostal') || '60-001',
                        width:    168,
                        height:   300,
                        color:    '#7CFC00'
                        };

                        const anchorHTML = `
                        <div class="card-publicacion-admin popup-fake-card">
                            <div class="dpia-popup-anchor"
                            data-dominio="${paramsPopup.dominio}"
                            data-categoria="${paramsPopup.categoria}"
                            data-lang="${paramsPopup.lang}"
                            data-cp="${paramsPopup.cp}"
                            data-width="${paramsPopup.width}"
                            data-height="${paramsPopup.height}"
                            data-placeholder-color="${paramsPopup.color}">
                            </div>
                        </div>`;




                        response.forEach(function(post) {
                            publicacionesValidas++;
                            if (post.imagenes.length > 0 || post.videos.length > 0) {
                                    var mediaHtml = '';

                                    // Mostrar la primera imagen
                                    if (Array.isArray(post.imagenes) && post.imagenes.length > 0  || post.videos.length > 0) {
                                        
                                        if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                                            // Si hay imágenes, usar la primera
                                            if (post.imagenes[0].imagen != null) {
                                                var firstImageBase64 = post.imagenes[0].imagen;
                                                var firstImageUrl = `data:${post.imagenes[0].mimetype};base64,${firstImageBase64}`;
                                                mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                        } else {
                                                var firstImageUrl = post.imagenes[0].filepath;
                    
                                                console.log(post.imagenes[0].filepath);
                                                mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                        }
                                        
                                        } else if (Array.isArray(post.videos) && post.videos.length > 0) {
                                        
                                            // Si no hay imágenes pero hay videos, usar el primero
                                            var firstVideoUrl = post.videos[0].filepath;
                                            console.log(post.videos[0].filepath);
                                        
                                            mediaHtml += `
                                                    <video controls  style="cursor: pointer;" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                                        <source src="${firstVideoUrl}" type="video/mp4">                                           
                                                        Tu navegador no soporta la reproducción de videos.
                                                    </video>
                                                `;

                                        } else {
                                            // Si no hay ni imágenes ni videos, mostrar un mensaje o imagen por defecto
                                            mediaHtml += `<p>No hay contenido multimedia disponible.</p>`;
                                        }

                                    
                                }

                                var estadoClass;
                                var estadoTextClass;
                            


                                //const { precio, descripcion } = extraerPrecioYDescripcion(post.texto);
                                const lang    = window.currentLang || 'es';
                                const vid     = getVisitorId();
                                const user_id = localStorage.getItem('usuario_id') || '';

                                const btnComprarAttrs = `
                                href="#"
                                class="btn btn-danger mt-2"
                                rel="nofollow sponsored"
                                data-ali-redirect="1"
                                data-pub-id="${post.publicacion_id}"
                                data-vid="${vid}"
                                data-user-id="${user_id}"
                                data-lang="${lang}"
                                `;

                            // Tarjeta
                                const comprarTxt = (translations[lang] && translations[lang].comprarAli) || 'Comprar';
                                const verMasTxt  = (translations[lang] && translations[lang].verMas) || 'Ver más';



                                var cardHtml = `
                                        <div class="card-publicacion-admin ${estadoClass}" id="card-${post.publicacion_id}">
                                            <div class="card-body">
                                                <a class="btn-close-publicacion" onclick="cerrarPublicacion(${post.publicacion_id})">
                                                    <span class="text-white">&times;</span>
                                                </a>
                                                <h5 class="card-title">${post.titulo}</h5>
                                                <div class="card-media-grid-publicacion-en-ambito">
                                                    ${mediaHtml}
                                                </div>
                                                <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                                <p class="card-text text-truncated" id="postText-${post.publicacion_id}">${post.texto}</p>
                                                <a href="#" class="btn-ver-mas" onclick="toggleTexto(${post.publicacion_id}); return false;">${verMasTxt}</a>

                                                <!-- Botón Afiliado -->
                                                ${post.afiliado_link ? `
                                                    <a href="#"
                                                    class="btn btn-danger mt-2"
                                                    rel="nofollow sponsored"
                                                    data-ali-redirect="1"
                                                    data-pub-id="${post.publicacion_id}"
                                                    data-vid="${vid}"
                                                    data-user-id="${user_id}"
                                                    data-lang="${lang}">
                                                    ${comprarTxt}
                                                    </a>` : ''}
                                            </div>
                                        </div>
                                    `;


                                postDisplayContainer.append(cardHtml);
                                   cardsRenderizadas++;

                                  // 👉 Intercalar popup como “falsa publicación”
                                  if (cardsRenderizadas % popupCada === 0) {
                                      
                                  // insertamos el anchor inmediatamente después de la card recién pintada
                                  $(`#card-${post.publicacion_id}`).after(anchorHTML);
                                  }
                                  // === PRUEBA: agrega 3 popups al final (como la que te funcionó) ===
                            } else {
                                splash.style.display = 'none'; // Ocultar el splash al terminar
                                console.log('Publicación sin contenido:', post.publicacion_id);
                            }
                        });



                          document.querySelectorAll('.dpia-popup-anchor').forEach(a => {
                                delete a.dataset.renderizado;
                                a.innerHTML = ''; // opcional: limpiar UI anterior
                                });

                                const cp        = localStorage.getItem('codigoPostal');
                                const dominio   = localStorage.getItem('dominio_id');
                                const categoria = localStorage.getItem('categoriaSeleccionadaId');
                                const lang      = localStorage.getItem('language');

                                window.initEmbedPopups({ cp, dominio, categoria, lang });


                    } else {
                        splash.style.display = 'none'; // Ocultar el splash al terminar
                        console.error("La respuesta no es un array. Recibido:", response);
                    }
                },
                error: function () {
                    splash.style.display = 'none'; // Ocultar el splash al terminar
                    console.error('Error al cargar la galería de imágenes.');
                }
            });


    }, 2000); // Esperamos 2 segundos para asegurar que `getLocation()` actualice `language`


}













document.addEventListener("DOMContentLoaded", function () {
    
    const botonCategorias = document.getElementById("caracteristicas-tab");

    if (botonCategorias) {
        botonCategorias.addEventListener("click", function () {
            const dropdownMenu = botonCategorias.parentElement.querySelector(".dropdown-menu");

            if (dropdownMenu) {
                dropdownMenu.innerHTML = "";  // Limpia todos los <li>
                console.log("Dropdown de categorías limpiado");

                const domain = localStorage.getItem('dominio');
                const selectedCategory = localStorage.getItem('categoria'); 

                // 🔁 USAR CACHE SI EXISTE
                if (categoriasCache[domain]) {
          //          console.log("⚡ Usando categorías en caché para:", domain);
                    renderizarCategorias(categoriasCache[domain], selectedCategory);
                } else {
           //         console.log("🌐 Cargando categorías desde servidor para:", domain);
                    cargarCategorias(domain, selectedCategory);
                }

            } else {
                console.warn("No se encontró el menú desplegable");
            }
        });
    }
});

function cargarCategorias(domain, selectedCategory) {
    //console.log("[INIT] Ejecutando cargarCategorias()");
   // console.log("➡️ Dominio (ámbito):", domain);
   // console.log("➡️ Categoría seleccionada:", selectedCategory);

    const cp = localStorage.getItem("codigoPostal") || "";
    const idioma = localStorage.getItem("language") || "in";

   // console.log("📦 Enviando datos:", { ambito: domain, cp: cp, idioma: idioma });

    fetch("/social-media-ambitosCategorias-categoria-mostrar/", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
            ambito: domain,
            cp: cp,
            idioma: idioma
        })
    })
    .then(response => {
       // console.log("✅ Respuesta recibida del backend:", response.status);
        return response.json();
    })
    .then(data => {
        //console.log("📨 Datos parseados del backend:", data);

        if (!data || !Array.isArray(data.categorias)) {
            console.error("[ERROR] La respuesta no contiene 'categorias' como array");
            return;
        }

        // 💾 Guardar en cache
        categoriasCache[domain] = data.categorias;

        renderizarCategorias(data.categorias, selectedCategory);
    })
    .catch(error => {
        console.error("[ERROR] Fallo al cargar categorías:", error);
    });
}

function renderizarCategorias(categorias, selectedCategory) {
    const dropdownMenu = document.querySelector('.categoria-dropdown-menu');
    if (!dropdownMenu) {
        console.warn("[ERROR] No se encontró el dropdown .categoria-dropdown-menu");
        return;
    }

    dropdownMenu.innerHTML = "";
    console.log(`🎯 Agregando ${categorias.length} categorías al dropdown`);
    
    categorias.forEach((categoria, index) => {
        const color = categoria.color || 'gray';

        const li = document.createElement("li");
        li.style.padding = "10px";

        const a = document.createElement("a");
        a.href = "#domains-publicaciones";       
        a.className = "categoria-dropdown-item";
        a.id = categoria.id;
        a.dataset.value = categoria.valor;
        a.dataset.color = color;
        a.style.color = color;
        a.style.padding = "10px";
        a.textContent = categoria.nombre;

        if (categoria.valor === selectedCategory) {
            a.classList.add("active");
        }

        li.appendChild(a);
        dropdownMenu.appendChild(li);

        const divider = document.createElement("li");
        divider.innerHTML = `<hr class="dropdown-divider">`;
        dropdownMenu.appendChild(divider);
    });

    if (dropdownMenu.lastChild?.tagName === 'LI') {
        dropdownMenu.lastChild.remove();
    }

    const botonCategorias = document.getElementById("caracteristicas-tab");
    const dropdownInstance = bootstrap.Dropdown.getOrCreateInstance(botonCategorias);
    dropdownInstance.show();

   // console.log("✅ Categorías agregadas correctamente al dropdown.");
}






















