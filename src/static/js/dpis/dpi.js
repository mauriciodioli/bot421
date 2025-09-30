// --- Logger central para ambitos ---
function logAmbitos(msg, extra) {
  const t = new Date().toISOString().split('T')[1].replace('Z','');
  console.log(`[ambitos ${t}] ${msg}`, extra || '');
}

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

const AMBITOS = {
  inFlight: false,
  lockReason: null,    // 'init' | 'cp' | 'lang'
  timer: null,
};

function setCookieOverwrite(name, value, days = 365) {
  const maxAge = days * 24 * 60 * 60;

  // Borro posibles valores previos
  document.cookie = `${name}=; path=/; max-age=0; samesite=lax`;
  document.cookie = `${name}=; max-age=0; samesite=lax`; // por si lo guardaron sin path

  // Escribo el nuevo valor
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/; max-age=${maxAge}; samesite=lax`;
}
document.addEventListener('DOMContentLoaded', function () {

    console.log("DOM listo");
    

//eventos para la carga de los items de los dominios
$(document).ready(function () {
    // Manejador de eventos para cada ítem del menú
  
    

    // Mostrar u ocultar el menú desplegable al hacer clic en el botón
    $('.close-layout-btn').on('click', function () {
        $('.dropdown-menu').toggle();
    });

    // Evitar que el menú se cierre cuando se haga clic dentro del contenedor
    $('.dropdown-menu').on('click', function(e) {
        e.stopPropagation(); // Evitar que se propague el clic y cierre el menú
    });

    // Cerrar el layout al hacer clic en el botón de cerrar
    $('#closeLayout').on('click', function () {
        $('#bottomLayout').addClass('hidden');
    });

    // Mantener la funcionalidad de mostrar/ocultar el layout con scroll
    let lastScrollTop = 0; // Última posición del scroll
    let scrolling = false; // Estado de scroll en curso

    $(window).on('scroll', function () {
        scrolling = true;

        // Obtener la posición actual del scroll
        const currentScrollTop = $(this).scrollTop();

        if (currentScrollTop > lastScrollTop) {
            // Scroll hacia abajo -> ocultar el layout
            $('#bottomLayout').addClass('hidden');
        } else {
            // Scroll hacia arriba -> mostrar el layout
            $('#bottomLayout').removeClass('hidden');
        }

        lastScrollTop = currentScrollTop; // Actualizar la última posición del scroll
    });

    // Comprobar si el usuario está en reposo (sin scroll) después de 2 segundos
    setInterval(function () {
        if (!scrolling) {
            $('#bottomLayout').removeClass('hidden'); // Mostrar el layout si no hay scroll
        }
        scrolling = false; // Reiniciar el estado de scroll
    }, 2000);
});

document.addEventListener("DOMContentLoaded", () => {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const dropdownContainer = document.getElementById("dropdownContainer");
    
    if (!dropdownButton || !dropdownMenu || !dropdownContainer) {
        console.error("Uno o más elementos no existen en el DOM.");
        return;
    }

    // Mostrar el menú al hacer clic en el botón
    dropdownButton.addEventListener("click", (event) => {
        event.stopPropagation(); // Evita que el clic cierre el menú
        dropdownMenu.style.display =
            dropdownMenu.style.display === "flex" ? "none" : "flex";
    });

    // Cerrar el menú cuando se haga clic fuera del contenedor
    document.addEventListener("click", () => {
        dropdownMenu.style.display = "none";
    });

    // Evitar que el menú se cierre al hacer clic dentro del contenedor
    dropdownContainer.addEventListener("click", (event) => {
        event.stopPropagation();
    });

    // Cerrar el menú al seleccionar un elemento
    dropdownMenu.querySelectorAll("a").forEach((item) => {
        item.addEventListener("click", () => {
            dropdownMenu.style.display = "none"; // Cerrar menú después de seleccionar un ítem
        });
    });
});

















// NO se declara ni se usa dropdownMenu en ningún lado

window.cargarAmbitos = function () {
  debugger;  
  return fetch('/social-media-publicaciones-obtener-ambitos/', {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  })
  .then(response => {
    if (!response.ok) throw new Error('Error al obtener los ámbitos.');
    return response.json();
  })
  .then(data => {
    const $cardContainer = $('.card-container');
    $cardContainer.empty();
debugger;
    // === Layout dentro de .card-container (no tocamos dropdown) ===
    const explore = `
      <section class="dpia-explore2" id="expertise">
        <div class="dpia-explore2__caption"><p>Domains</p></div>
        <div class="dpia-explore2__grid">
          <nav class="dpia-explore2__nav" aria-label="Domains">
            <ul id="dx-nav"><!-- items dinámicos --></ul>
          </nav>

          <div class="dpia-explore2__content">
            <div class="dpia-explore2__pill is-active" id="dx-active-pill"></div>
            <p class="dpia-explore2__desc" id="dx-desc"></p>
            <a class="dpia-explore2__more" id="dx-more" href="#domains-publicaciones" target="_self">
              See more <span class="dx-more-ico"></span>
            </a>
            <div class="dpia-explore2__pills" id="dx-other-pills"></div>

            <!-- Ghost cards para compatibilidad -->
            <div class="card-compat" aria-hidden="true" style="display:none" id="card-compat-container"></div>
          </div>
        </div>
      </section>`;
    $cardContainer.append(explore);

    // === Data normalizada DOMAINS ===
    const DOMAINS = data.map((a, index) => {
      const img = (a.imagen && a.imagen.trim())
        || (window.imgByValor ? window.imgByValor[index] : null)
        || '/static/img/images_dpi_tarjetas2.jpg';

      const fb = (window.DOMAINS_FALLBACKS && window.DOMAINS_FALLBACKS[a.valor]) || {};
      return {
        key:  a.valor,
        id:   a.id,
        name: a.nombre,
        desc: (a.descripcion && a.descripcion.trim()) || fb.desc || '—',
        href: (a.url && a.url.trim()) || fb.href || '#domains-publicaciones',
        img
      };
    }).filter(d => d.key && d.name);

    const $nav    = $('#dx-nav');
    const $pill   = $('#dx-active-pill');
    const $desc   = $('#dx-desc');
    const $more   = $('#dx-more');
    const $others = $('#dx-other-pills');
    const $compat = $('#card-compat-container');

    function renderNav(activeKey){
      $nav.html(DOMAINS.map(d => `
        <li>
          <button
            class="${d.key===activeKey?'is-active':''}"
            data-key="${d.key}"
            id="card-${d.key}"
            data-id="${d.id}"
            style="--card-bg:url('${d.img}')">
            <span class="card-number">${d.name}</span>
            <span class="dx-arrow"></span>
            <input type="hidden" class="ambito-id-oculto" value="${d.id}">
          </button>
        </li>`).join(''));
    }

    function renderCompatGhost(){
      $compat.html(DOMAINS.map((d, idx) => `
        <div class="numRequeris-card${idx+1} card card--bg"
             id="card-${d.key}"
             data-id="${d.id}"
             style="--card-bg:url('${d.img}')">
          <div class="card-content">
            <p class="card-number">${d.name}</p>
            <input type="hidden" class="ambito-id-oculto" value="${d.id}">
          </div>
        </div>`).join(''));
    }

    function renderContent(activeKey){
      const active = DOMAINS.find(d=>d.key===activeKey) || DOMAINS[0];
      if(!active) return;

      $pill.text(active.name);
      $desc.text(active.desc);
      $more.attr('href', active.href || '#domains-publicaciones');

      const others = DOMAINS.filter(d=>d.key!==activeKey);
      $others.html(others.map(d => `
        <button class="pill"
                data-key="${d.key}"
                data-id="${d.id}"
                style="--card-bg:url('${d.img}')">
          <span class="card-number">${d.name}</span>
          <input type="hidden" class="ambito-id-oculto" value="${d.id}">
        </button>`).join(''));
    }

    function setActive(key){
      renderNav(key);
      renderContent(key);
    }

    function seleccionarDominio(nombre, id){
      const limpio = (nombre || '').replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();
        debugger;
      localStorage.setItem('dominio', limpio);
      setCookieOverwrite('dominio', nombre);
      setCookieOverwrite('dominioValor', nombre);
      if (id !== undefined && id !== null) {
        localStorage.setItem('dominio_id', id);
        document.cookie = `dominio_id=${id}; path=/; max-age=31536000`;
      }

      const hiddenInput = $('#domain');
      if (hiddenInput.length) hiddenInput.val(limpio);

      console.log('Dominio seleccionado:', limpio, 'ID:', id);
      if (typeof cargarCategoriasEnPills === 'function') cargarCategoriasEnPills();

      $nav.find('button').removeClass('is-active');
      $nav.find(`button[data-key="${(DOMAINS.find(d=>d.name===nombre)?.key)||''}"]`).addClass('is-active');
      $others.find('button').removeClass('active');
      $others.find(`button:contains("${nombre}")`).addClass('active');

      $('#ambitoActual').focus();
    }

    if (DOMAINS.length){
      renderCompatGhost();
      setActive(DOMAINS[0].key);
    }

    // Eventos internos (nav/pills)
    $nav.on('click', 'button[data-key]', function(){
      const key = $(this).data('key');
      const d = DOMAINS.find(x=>x.key===key);
      if(!d) return;
      setActive(key);
      seleccionarDominio(d.name, d.id);
    });

    $others.on('click', 'button[data-key]', function(){
      const key = $(this).data('key');
      const d = DOMAINS.find(x=>x.key===key);
      if(!d) return;
      setActive(key);
      seleccionarDominio(d.name, d.id);
    });

    // Aviso para otros módulos: datos listos (por si otro archivo sí quiere pintar el dropdown)
    window.dispatchEvent(new CustomEvent('ambitos:cargados', { detail: { DOMAINS, raw: data } }));

    return { DOMAINS, raw: data };
  })
  .catch(error => {
    console.error('Error al cargar los ámbitos:', error);
  });
};

// Delegación tarjetas (esto no toca dropdown)
$('.card-container').on('click', '.card', function () {
  const selectedDomain = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();
  const selectedDomainId = $(this).data('id');
debugger;
  localStorage.setItem('dominio', selectedDomain);
  localStorage.setItem('dominio_id', selectedDomainId);
  document.cookie = `dominio_id=${selectedDomainId}; path=/; max-age=31536000`;

  const hiddenInput = $('#domain');
  if (hiddenInput.length) hiddenInput.val(selectedDomain);

  console.log('Dominio seleccionado:', selectedDomain, 'ID:', selectedDomainId);
  if (typeof enviarDominioAJAX === 'function') enviarDominioAJAX(selectedDomain);

  $('.card').removeClass('active');
  $(this).addClass('active');
  $('#ambitoActual').focus();
});
debugger;
// Cargar al inicio (no toca dropdown)


localStorage.setItem('banderaCategorias', 'True');

});


















 
 
 
 
 // Obtener el enlace "Signals"
const btnSignals = document.getElementById('openModalSignals');
if (btnSignals) {
  btnSignals.addEventListener('click', function (e) {
    e.preventDefault();
    const modalSeleccionPais = new bootstrap.Modal(
      document.getElementById('modalSeleccionPais')
    );
    modalSeleccionPais.show();
  });
}

 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
document.addEventListener("DOMContentLoaded", function() {
    cargaCodigoPostalLayout();
});
 
 function cargaCodigoPostalLayout(){
    // Obtener referencia al label
    const labelCP = document.getElementById("labelCP");

    // Obtener el valor almacenado en localStorage
    const cpValue = localStorage.getItem("codigoPostal");

    // Si hay un valor en localStorage, asignarlo al label
    if (cpValue) {
        labelCP.textContent = cpValue;
    }
 

 }
 


// Obtener el enlace "Signals"
document.getElementById('openModalCP').addEventListener('click', function (e) {
    // Prevenir el comportamiento por defecto (enlace)
    e.preventDefault();
    
    // Cargar el código postal desde el localStorage si existe
    const codigoPostalGuardado = localStorage.getItem('codigoPostal');
    if (codigoPostalGuardado) {
        // Mostrar el código postal guardado en el campo del modal
        document.getElementById('codigoPostalModal').value = codigoPostalGuardado;
    } else {
        // Si no hay código postal en localStorage, dejar el campo vacío
        document.getElementById('codigoPostalModal').value = '';
    }

    // Abrir el modal
    var myModal = new bootstrap.Modal(document.getElementById('modalSeleccionCodigoPostal'));
    myModal.show();
});




// Función para guardar el código postal en el localStorage
// Función para guardar el código postal en el localStorage y las cookies
function guardarCodigoPostal() {
    const codigoPostal = document.getElementById('codigoPostalModal').value;
   
    // Validar si el campo no está vacío y contiene solo números
    if (codigoPostal) {
        // Guardar el código postal en el localStorage
        localStorage.setItem('codigoPostal', codigoPostal);
        console.log('Código Postal guardado en localStorage:', codigoPostal);

        // Guardar el código postal en las cookies (con una duración de 1 hora)
        document.cookie = `codigoPostal=${codigoPostal};max-age=3600;path=/`;
        cargaCodigoPostalLayout();
        // Cerrar el modal
        const myModal = bootstrap.Modal.getInstance(document.getElementById('modalSeleccionCodigoPostal'));
        myModal.hide();  // Aquí se cierra el modal
        debugger;
        triggerAmbitosReload();


    } else {
        alert('Por favor ingresa un código postal válido (solo números)');
    }
}
//document.addEventListener('DOMContentLoaded', function() {
    // Función para permitir solo números en el input
  //  document.getElementById('codigoPostalModal').addEventListener('input', function(event) {
        // Reemplazar todo lo que no sea un número
    //    event.target.value = event.target.value.replace(/[^0-9]/g, '');
    //});
//});



document.addEventListener('DOMContentLoaded', () => {
  const btnGuardarPais = document.getElementById('guardarPais');

  if (btnGuardarPais) {
    btnGuardarPais.addEventListener('click', function () {
      document.getElementById('splash').style.display = 'block';

      const selectedCountry = document.getElementById('seleccionarPais').value;
      localStorage.setItem('paisSeleccionado', selectedCountry);

      const usuario_id = 'demo';
      const access_token = 'access_dpi_token_usuario_anonimo';
      const refresh_token = 'access_dpi_refresh_token';
      const selector = localStorage.getItem('selector');

      $('#modalSeleccionPais').modal('hide');

      const layoutOrigen = 'layout_dpi';
      const url = `/panel_control_sin_cuenta/?country=${selectedCountry}&layoutOrigen=${layoutOrigen}&usuario_id=${usuario_id}&access_token=${access_token}&refresh_token=${refresh_token}&selector=${selector}`;
      
      console.log("Enviando AJAX");
      window.location.href = url;
    });
  } else {
    console.warn("No se encontró el elemento con ID 'guardarPais'.");
  }
});


function cargarOpcionesCombo() {

// Realizar una solicitud Ajax para obtener las opciones del combo
fetch('/cuenta-endpoint-all/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        accessToken: access_token // Reemplaza 'TOKEN_AQUI' con el token adecuado
    })
})
.then(response => response.json())
.then(data => {
    const selectElement = document.getElementById('selctorEnvironment1');
    // Limpiar las opciones existentes
    selectElement.innerHTML = '';

    // Agregar la opción inicial
    const initialOption = document.createElement('option');
    initialOption.value = ''; // Opcional: puedes asignar un valor específico aquí si lo necesitas
    initialOption.textContent = 'Open this select menu';
    selectElement.appendChild(initialOption);

    // Agregar las nuevas opciones desde los datos obtenidos
    data.endpoints.forEach(endpoint => {
        const optionElement = document.createElement('option');
        optionElement.value = endpoint.id; // Cambiar por el valor correcto
        optionElement.textContent = endpoint.nombre; // Cambiar por el texto correcto
        selectElement.appendChild(optionElement);
    });

    // Agregar un event listener para el cambio en el selector de entorno
    selectElement.addEventListener('change', function() {
        // Obtener el valor y el texto seleccionados
        const selectedOption = this.options[this.selectedIndex];
        const brokerId = selectedOption.value;
        const brokerNombre = selectedOption.textContent;

        // Actualizar los campos ocultos con los valores seleccionados
        document.getElementById('broker_id').value = brokerId;
        document.getElementById('broker_nombre').value = brokerNombre;
    });
})
.catch(error => {
  console.error('Error al cargar opciones del combo:', error);
  alert('Hubo un problema al cargar las opciones del combo. Por favor, logee nuevamente en el sistema puede haber vencido el token de acceso o inténtalo de nuevo más tarde o contacta al soporte técnico.');
});
}



// Llamar a la función para cargar las opciones del combo cuando la página se cargue
//window.addEventListener('DOMContentLoaded', cargarOpcionesCombo);














//carga inicialmente un dominio y luego con el clic de la barra de herramientas





// Realizar la solicitud AJAX al cargar la página
$(document).ready(function () {
  
  // dominio desde localStorage o desde la URL /index/<dominio>
  let domain = localStorage.getItem('dominio');
  if (!domain || domain === 'null') {
    const currentURL = window.location.href;
    let partAfterIndex = (currentURL.split('index/')[1] || '').trim();
    if (!partAfterIndex) partAfterIndex = 'Laboral';
    
    localStorage.setItem('dominio', domain);
  }

  // mostrar spinner (solo mobile)
  showGlobalSpinner();

  // lanzar tu carga inicial
  const maybePromise = enviarDominioAJAX(domain);

  // apagar spinner al terminar (funcione devuelva promesa o no)
  if (maybePromise && typeof maybePromise.finally === 'function') {
    maybePromise.finally(hideGlobalSpinner);
  } else {
    $(document).one('ajaxStop', hideGlobalSpinner); // fallback jQuery
  }
});



// Define la función formatDate
function formatDate(dateString) {
  var options = { year: 'numeric', month: 'long', day: 'numeric' };
  var date = new Date(dateString);
  return date.toLocaleDateString(undefined, options);
}



// Función para verificar si la sección es visible en la ventana
function isSectionVisible(section) {
    const sectionRect = section.getBoundingClientRect();
    return (
        sectionRect.top < (window.innerHeight || document.documentElement.clientHeight) &&
        sectionRect.bottom > 0
    );
}

// Función para mostrar/ocultar el splash
function toggleSplash(section, splashElement) {
    const splashHeight = 80;  // Altura fija del splash en píxeles

    if (isSectionVisible(section)) {
        splashElement.style.display = "flex"; // Mostrar el splash
        splashElement.style.position = "relative"; // Usamos relative para que se acomode sin afectar el flujo
        splashElement.style.height = `${splashHeight}px`; // Fijar la altura del splash
        splashElement.style.top = "0";  // Colocar el splash al principio de la sección
        splashElement.style.left = "0"; // Asegurarse de que ocupe todo el ancho de la sección
        splashElement.style.width = "100%"; // Asegurarse de que solo ocupe el ancho de la sección
        splashElement.style.backgroundColor = "transparent"; // Fondo transparente

        // Asegurarse de que el splash ocupe un espacio adecuado en la página
        section.style.paddingTop = `${splashHeight + 20}px`;  // Dejar espacio suficiente arriba de la sección
        section.style.paddingBottom = "20px";  // Añadir un pequeño espacio debajo si lo necesitas
    } else {
        splashElement.style.display = "none"; // Ocultar el splash
        // Restablecer el padding de la sección cuando el splash no esté visible
        section.style.paddingTop = "0";
        section.style.paddingBottom = "0";
    }
}
let ajaxInProgress = false;

function enviarDominioAJAX(domain) {
    if (ajaxInProgress) {
        console.log("AJAX ya en curso, evitando llamada duplicada");
        return; // Evita llamadas simultáneas
    }
    ajaxInProgress = false;
    console.log("Dominio:", domain);
    localStorage.setItem('banderaCategorias', 'True');
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
        debugger;
        localStorage.setItem('dominio', domain);
        let ambito_actual = "<a ' style='text-decoration:none; '>" + domain + "</a>";
        document.getElementById("ambitoActual").innerHTML = ambito_actual;
    }

    if ( domain !=='inicialDominio') {
          debugger;
        localStorage.setItem('dominio', domain);
        let ambito_actual = "<a ' style='text-decoration:none; '>" + domain + "</a>";
        document.getElementById("ambitoActual").innerHTML = ambito_actual;
    }


    domain = localStorage.getItem('dominio');
    let ambito_actual = "<a ' style='text-decoration:none;'>" + domain + "</a>";
    document.getElementById("ambitoActual").innerHTML = ambito_actual;
    // Obtener ubicación antes de ejecutar AJAX
    let existe = localStorage.getItem('language');

    if (!existe){
        getLocation();
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
                        codigoPostal: cp,                         
                        lenguaje: lenguaje}, // Enviar el dominio como parte de los datos
                success: function (response) {
                    
                    $('#ambitoActual').focus();
                        console.log("Respuesta del servidor:", response);
                    if (response.length == 0) {
                        splash.style.display = 'none'; // Ocultar el splash al terminar
                        return;
                    }
                // console.log('Respuesta del servidor:', response[0].ambito);
                    if (response && response[0]) {
                        document.getElementById("ambitoActual").innerHTML = response[0].ambito;
                    } else {
                        console.error("La respuesta del servidor no contiene el formato esperado.");
                    }
                     // Verificar si existe un 'codigoPostal' en localStorage
                    let codigoPostal = localStorage.getItem('codigoPostal');
                    if (codigoPostal) {
                        // Crear la cookie con el código postal
                        document.cookie = `codigoPostal=${codigoPostal}; path=/; max-age=86400`; // Expira en 1 día
                    }
                    splash.style.display = 'none'; // Ocultar el splash al terminar
                    
                    if (Array.isArray(response)) {
                        var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                        postDisplayContainer.empty();

                        response.forEach(function(post) {
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
                                                <!-- Precios -->
                                                ${post.precio_original ? `<p class="precio-original text-muted" style="text-decoration: line-through; font-size: 0.95rem;">${post.precio_original}</p>` : ''}
                                                ${post.precio ? `<p class="card-precio text-success fw-bold" style="font-size: 1.2rem;">${post.simbolo}${post.precio}</p>` : ''}

                                                <p class="card-text text-truncated" id="postText-${post.publicacion_id}">${post.texto}</p>
                                                <a href="#" class="btn-ver-mas" onclick="toggleTexto(${post.publicacion_id}); return false;">Ver más</a>
                                                <!-- Botón Afiliado -->
                                                    ${post.afiliado_link ? `
                                                        <a href="${post.afiliado_link}" target="_blank" class="btn btn-danger mt-2">
                                                            ${translations[currentLang].comprarAli}
                                                        </a>
                                                    ` : ''}
                                                
                                            </div>
                                        </div>
                                    `;


                                postDisplayContainer.append(cardHtml);
                            } else {
                                splash.style.display = 'none'; // Ocultar el splash al terminar
                                console.log('Publicación sin contenido:', post.publicacion_id);
                            }
                        });
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



function cerrarPublicacion(publicacionId) {
  var access_token = localStorage.getItem('access_token');

  // Enviar solicitud AJAX para actualizar el estado de la publicación
  $.ajax({
      url: '/social_media_publicaciones_borrado_logico_publicaciones/', // Asegúrate de que esta URL sea correcta
      type: 'POST',
      headers: {
          'Authorization': 'Bearer ' + access_token // Agregar el token al encabezado Authorization
      },
      data: {
          id: publicacionId,
          estado: 'eliminado' // Actualizar el estado
      },
      success: function(response) {
          if (response.success) {
              // Eliminar la tarjeta del DOM si la solicitud fue exitosa
              $(`#card-${publicacionId}`).remove();
          } else {
              alert('Error al eliminar la publicación.');
          }
      },
      error: function(xhr, status, error) {
          alert('Error al enviar la solicitud. Inténtalo de nuevo.');
      }
  });
}



function toggleTexto(postId) {
  var postText = document.getElementById(`postText-${postId}`);
  var button = document.querySelector(`#card-${postId} .btn-ver-mas`);
  
  if (button) { // Verifica si el botón existe
      if (postText.classList.contains('text-truncated')) {
          postText.classList.remove('text-truncated');
          postText.classList.add('text-expanded');
          button.textContent = 'Ver menos';
      } else {
          postText.classList.remove('text-expanded');
          postText.classList.add('text-truncated');
          button.textContent = 'Ver más';
      }
  } else {
      console.error(`No se encontró el botón para el postId: ${postId}`);
  }
}


function abrirPublicacionHome(publicacionId) {
    // Mostrar el splash de carga
    const splash = document.querySelector('.splashCarga');
    const targetSection = document.querySelector('.dpi-muestra-publicaciones-centrales'); // Asegúrate de que esta clase esté bien definida

    if (!splash || !targetSection) {
        console.error("No se encontró el elemento 'splashCarga' o la sección 'dpi'.");
        return;
    }

    toggleSplash(targetSection, splash);
    console.log("Enviando AJAX");
   // Redirigir al usuario a una nueva página que muestra todos los detalles de la publicación
    window.location.href = `/${publicacionId}`;
}


// Asegurar que el splash desaparezca al volver atrás
window.addEventListener("pageshow", function(event) {
    var splash = document.querySelector('.splashCarga');

    if (splash) {
        // Si la página se cargó desde la caché del navegador (back-forward cache)
        if (event.persisted) {
            splash.style.display = 'none';
        }
    }
});








// Función para obtener el valor de una cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Obtener el idioma del navegador (si no se encuentra en cookies o en la ubicación)
var currentLanguage = navigator.language.split('-')[0].toLowerCase(); 

// Obtener el enlace para cambiar el idioma
const languageLink = document.getElementById("languageLink");
// dpi.js (u otros)
(function () {
  const el = (window.dpia && window.dpia.languageLink) || document.getElementById('languageLink');
  if (!el) return; // en esta vista no está, salimos sin romper nada
  // …tu lógica usando `el`…
})();


document.addEventListener("DOMContentLoaded", function () {
    
    // Si no existe la cookie "language", intenta obtener la ubicación y luego establecer el idioma
   
    // Intenta obtener la ubicación
    //getLocation();  // Llama a getLocation, que debe establecer el idioma basado en la ubicación
  
    setTimeout(function() {
        // Si existe la cookie, usa el idioma configurado en ella
        currentLanguage = localStorage.getItem("language") || getCookie("language");
    
        // Cambiar el texto del enlace según el idioma
        
        // Si no se pudo obtener el idioma desde las cookies o la ubicación, usa el idioma del navegador
        if (!currentLanguage) {
            
            currentLanguage = navigator.language.split('-')[0].toLowerCase();
            

            // Establecer el idioma en las cookies y el almacenamiento local
            document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`; // Validez de 1 año
            localStorage.setItem("language", currentLanguage);

        }

       if (languageLink) {
                languageLink.textContent = currentLanguage;
        }

    }, 1000); // 1000 milisegundos = 1 segundo
});




document.addEventListener("DOMContentLoaded", function () {
    const selector = document.getElementById("languageSelector");
    const selected = selector.querySelector(".selected-language");
    const dropdown = selector.querySelector(".language-dropdown");

    const languages = {
        in: { name: "English", code: "ENG", flag: "https://flagcdn.com/24x18/us.png" },
        pl: { name: "Poland", code: "PL", flag: "https://flagcdn.com/24x18/pl.png" },       
        fr: { name: "Français", code: "FR", flag: "https://flagcdn.com/24x18/fr.png" },
        es: { name: "Español", code: "ES", flag: "https://flagcdn.com/24x18/es.png" },
        de: { name: "Deutsch", code: "DE", flag: "https://flagcdn.com/24x18/de.png" },
        it: { name: "Italiano", code: "IT", flag: "https://flagcdn.com/24x18/it.png" },
        pt: { name: "Português", code: "PT", flag: "https://flagcdn.com/24x18/pt.png" }
       
    };

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : null;
    }

    function setLanguage(lang) {
        const langData = languages[lang];
        if (!langData) return;

        localStorage.setItem("language", lang);
        document.cookie = `language=${lang}; path=/; max-age=31536000`;

        selected.innerHTML = `<img src="${langData.flag}"> ${langData.code}`;
        dropdown.style.display = "none";
        debugger;
        triggerAmbitosReload();

    }

    function buildDropdown() {
        dropdown.innerHTML = "";
        for (const [code, lang] of Object.entries(languages)) {
            const option = document.createElement("div");
            option.className = "language-option";
            option.innerHTML = `<img src="${lang.flag}"> ${lang.name}`;
            option.addEventListener("click", () => setLanguage(code));
            dropdown.appendChild(option);
        }
    }

    selected.addEventListener("click", () => {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
        if (!selector.contains(e.target)) {
            dropdown.style.display = "none";
        }
    });

    const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
    setLanguage(currentLang);
    buildDropdown();
});


























// === utilidades en GLOBAL ===
window.showGlobalSpinner = function(){
  const el = document.getElementById('globalSpinner');
  if (!el) return;
  if (el.parentElement !== document.body) document.body.appendChild(el);
  el.style.display = 'flex';
  document.body.style.overflow = 'hidden';
};
window.hideGlobalSpinner = function(){
  const el = document.getElementById('globalSpinner');
  if (!el) return;
  el.style.display = 'none';
  document.body.style.overflow = '';
};






let _ambitosReloadTimer = null;

// Llamá SIEMPRE esto en vez de cargarAmbitos() directo
function triggerAmbitosReload(reason, delayMs = 100) {
  // si hay otra razón en curso, ignorar
  if (AMBITOS.lockReason && AMBITOS.lockReason !== reason) {
    logAmbitos(`skip (${reason}) lock=${AMBITOS.lockReason}`);
    return;
  }
  AMBITOS.lockReason = reason;

  clearTimeout(AMBITOS.timer);
  AMBITOS.timer = setTimeout(async () => {
    if (AMBITOS.inFlight) { logAmbitos(`skip (${reason}) inFlight`); return; }
    AMBITOS.inFlight = true;
    logAmbitos(`FETCH start by ${reason}`);

    try {
      // tu función actual que hace el fetch y pinta la UI:
      // debe devolver una promesa
      const res = await cargarAmbitos();

      // si tu carrusel usa el MISMO endpoint, no hagas otro GET:
      // si tenés una versión que recibe los datos, úsala aquí
      if (typeof cargarAmbitosCarruselFromData === 'function' && res?.raw) {
        cargarAmbitosCarruselFromData(res.raw);
      }
    } catch (e) {
      console.warn('[ambitos] error:', e);
    } finally {
      AMBITOS.inFlight = false;
      logAmbitos(`FETCH end by ${reason}`);
      // liberá el lock un toque después para evitar carreras
      setTimeout(() => { AMBITOS.lockReason = null; }, 150);
    }
  }, delayMs);
}
