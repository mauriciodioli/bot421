
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

















            
        const dropdownMenu = document.querySelector('.dropdown-menu');

        // Función para cargar los ámbitos desde el servidor
        window.cargarAmbitos = function () {
        
            fetch('/social-media-publicaciones-obtener-ambitos/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al obtener los ámbitos.');
                }
                return response.json();
            })
            .then(data => {
                const dropdownMenu = $('.dropdown-menu'); // Usar jQuery para seleccionar el menú
                const cardContainer = $('.card-container'); // Usar jQuery para seleccionar el contenedor de tarjetas

                // Limpiar el menú existente
                dropdownMenu.empty();
                // Limpiar el contenedor de tarjetas
                cardContainer.empty();  // Limpiar antes de agregar las nuevas tarjetas

                // Agregar los ámbitos dinámicamente al menú
                data.forEach((ambito, index) => {
                    // Agregar el ámbito al menú desplegable
                    const listItem = `
                        <li>
                            <a href="#" class="dropdown-item" id="${ambito.valor}">
                                ${ambito.nombre}
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                    `;
                    dropdownMenu.append(listItem);

                    // Crear una nueva tarjeta para cada dominio
                    const domainCard = `
                        <div class="numRequeris-card${index + 1} card" id="card-${ambito.valor}">
                            <div class="card-content">                              
                                <p class="card-number">${ambito.nombre}</p>
                            </div>
                        </div>
                    `;

                    // Insertar la tarjeta en el contenedor
                    cardContainer.append(domainCard); // Usar jQuery para insertar la tarjeta
                });

                // Agregar el elemento "Turing test" al final del menú
                const turingTestItem = `
                    <li class="nav-item content">
                        <a class="nav-link active" style="color: black;" href="/turing-testTuring">Turing test</a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                `;
                dropdownMenu.append(turingTestItem);

                // Eliminar el último separador
                dropdownMenu.children('li').last().remove();
            })
            .catch(error => {
                console.error('Error al cargar los ámbitos:', error);
            });
        }

        // Delegación de eventos para manejar clics en los ítems del menú desplegable
        $('.dropdown-menu').on('click', '.dropdown-item', function (e) {
            e.preventDefault(); // Previene el comportamiento predeterminado

            const selectedDomain = this.id; // ID del ítem clickeado

            // Guardar el dominio en localStorage
            localStorage.setItem('dominio', selectedDomain);

            // Actualizar el input oculto
            const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
            if (hiddenInput.length) {
                hiddenInput.val(selectedDomain);
            }

            // Mostrar en consola
            console.log('Dominio seleccionado:', selectedDomain);
            
            // Llamar a la función para manejar el dominio seleccionado
            enviarDominioAJAX(selectedDomain);

            // Marcar el ítem como activo
            $('.dropdown-item').removeClass('active');
            $(this).addClass('active');
        });

        // Delegación de eventos para manejar clics en las tarjetas
        $('.card-container').on('click', '.card', function () {
            //const selectedDomain = $(this).find('.card-number').text(); // Usar el número de la tarjeta como dominio
            const selectedDomain = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();

            // Guardar el dominio en localStorage
            localStorage.setItem('dominio', selectedDomain);

            // Actualizar el input oculto
            const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
            if (hiddenInput.length) {
                hiddenInput.val(selectedDomain);
            }

            // Mostrar en consola
            console.log('Dominio seleccionado:', selectedDomain);
            
            // Llamar a la función para manejar el dominio seleccionado
            enviarDominioAJAX(selectedDomain);

            // Marcar la tarjeta como activa
            $('.card').removeClass('active');
            $(this).addClass('active');


             
            // Enfocar la sección
            $('#ambitoActual').focus();
        });

        // Llamar a la función para cargar los ámbitos al cargar la página
        
        cargarAmbitos();
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
  // Obtener el valor por defecto del input hidden cuando carga la página
  
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
    enviarDominioAJAX(domain);
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
        
        localStorage.setItem('dominio', domain);
        let ambito_actual = "<a ' style='text-decoration:none; color:orange;'>" + domain + "</a>";
        document.getElementById("ambitoActual").innerHTML = ambito_actual;
    }

    if ( domain !=='inicialDominio') {
        
        localStorage.setItem('dominio', domain);
        let ambito_actual = "<a ' style='text-decoration:none; color:orange;'>" + domain + "</a>";
        document.getElementById("ambitoActual").innerHTML = ambito_actual;
    }


    domain = localStorage.getItem('dominio');
    let ambito_actual = "<a ' style='text-decoration:none; color:orange;'>" + domain + "</a>";
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
    window.location.href = `/media-muestraPublicacionesEnDpi-mostrar/${publicacionId}`;
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

        if (typeof cargarAmbitos === "function") cargarAmbitos();
        if (typeof cargarAmbitosCarrusel === "function") cargarAmbitosCarrusel();
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


















