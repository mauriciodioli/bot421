
document.addEventListener('DOMContentLoaded', function () {

    
    

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
    window.cargarAmbitos = function ()  {
        fetch('/social-media-publicaciones-obtener-ambitos', {
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
                const dropdownMenu = $('.dropdown-menu'); // Usa jQuery para seleccionar el menú

                // Limpiar el menú existente
                dropdownMenu.empty();

                // Agregar los ámbitos dinámicamente al menú
                data.forEach(ambito => {
                    const listItem = `
                        <li>
                            <a href="#" class="dropdown-item" id="${ambito.valor}">
                                ${ambito.nombre}
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                    `;
                    dropdownMenu.append(listItem);
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

    // Delegación de eventos para manejar clics en los ítems
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

        // Cerrar el menú (opcional)
       // $(this).closest('.dropdown-menu').hide();
    });

    
    // Llamar a la función para cargar los ámbitos al cargar la página
    cargarAmbitos();
});


















 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 // Obtener el enlace "Signals"
 document.getElementById('openModalSignals').addEventListener('click', function (e) {
    // Prevenir el comportamiento por defecto (enlace)
    e.preventDefault();
    // Abrir el modal
    var myModal = new bootstrap.Modal(document.getElementById('modalSeleccionPais'));
    myModal.show();
});




function mostrarSplash() {
    document.getElementById("splash").style.display = "block";
  }

  document.getElementById('guardarPais').addEventListener('click', function() {
    document.getElementById('splash').style.display = 'block';
   
    var selectedCountry = document.getElementById('seleccionarPais').value;
    localStorage.setItem('paisSeleccionado',selectedCountry)
    var usuario_id ='demo';
    access_token = 'access_dpi_token_usuario_anonimo';
    refresh_token = 'access_dpi_refresh_token';
    var selector = localStorage.getItem('selector');
    localStorage.setItem('paisSeleccionado', selectedCountry);
    $('#modalSeleccionPais').modal('hide'); // Esta línea cierra el modal
     // Redirigir a la ruta /panel_control_sin_cuenta
    layoutOrigen = 'layout_dpi'; // Cambia 'nombre_del_layout' por el valor deseado
    var url = '/panel_control_sin_cuenta?country=' + selectedCountry + '&layoutOrigen=' + layoutOrigen+ '&usuario_id=' + usuario_id+'&access_token='+access_token+'&refresh_token='+refresh_token+'&selector='+selector;
    window.location.href = url;
  });   
// en este script cargo el correo electrónico almacenado en el localStorage
access_token = 'access_dpi';
correo_electronico = 'desde_dpi_acceso_anonimo';

$(document).ready(function() {
// Escuchar el evento de cambio en el combobox 1
$("#selctorEnvironment1").change(function() {
  // Obtener el valor seleccionado
  
  var selectedValue = $(this).val();


  // Asignar el valor al campo de entrada oculto "environment" en el formulario 1
  $("input[name='broker_id']").val(selectedValue);
});

// Escuchar el evento de cambio en el combobox 2
$("#selctorEnvironment2").change(function() {
  // Obtener el valor seleccionado
  var selectedValue2 = $(this).val();
 

  // Asignar el valor al campo de entrada oculto "environment" en el formulario 2
  $("input[name='environment']").val(selectedValue2);
});

// Asignar el valor del access token al campo oculto en ambos formularios
$("input[name='access_token']").val(access_token);
$("input[name='access_token_form2']").val(access_token);
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
            partAfterIndex = 'laboral';
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

function enviarDominioAJAX(domain) {
 
    // Elementos relevantes
    const splash = document.querySelector('.splashCarga');
    const targetSection = document.querySelector('.dpi-muestra-publicaciones-centrales'); // Asegúrate de que esta clase esté bien definida

    if (!splash || !targetSection) {
        console.error("No se encontró el elemento 'splashCarga' o la sección 'domains'.");
        return;
    }

    // Mostrar/ocultar splash según la visibilidad de la sección
    toggleSplash(targetSection, splash);

    // Ruta al archivo con la galería de imágenes
    var galeriaURL = '/MostrarImages/';
    var galeriaURL1 = '/media-publicaciones-mostrar-dpi';
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

    $.ajax({
    type: 'POST',
    url: galeriaURL1,
    dataType: 'json', // Asegúrate de que el backend devuelva un JSON
    headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
    data: { ambitos: domain }, // Enviar el dominio como parte de los datos
    success: function (response) {
    
        splash.style.display = 'none'; // Ocultar el splash al terminar
        if (Array.isArray(response)) {
            var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
            postDisplayContainer.empty();

            response.forEach(function(post) {
                if (post.imagenes.length > 0 || post.videos.length > 0) {
                    var mediaHtml = '';
                    //var baseUrl = window.location.origin;

                    if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                        // Mostrar solo la primera imagen
                        //var firstImageUrl = baseUrl + '/' + post.imagenes[0].filepath;
                        var firstImageUrl = post.imagenes[0].filepath;
                        mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id})" style="cursor: pointer;">`;

                        // Guardar las demás imágenes para mostrarlas en el modal
                        var modalImagesHtml = '';
                        post.imagenes.forEach(function(image, index) {
                            if (index > 0) { // Saltar la primera imagen
                                //var imageUrl = baseUrl + '/' + image.filepath;
                                var imageUrl = image.filepath;
                                modalImagesHtml += `<img src="${imageUrl}" alt="Imagen de la publicación" class="imagen-muestra-en-ambito-publicacion">`;
                            }
                        });

                        // Crear el HTML del modal con el sufijo muestra-crea-publicacion
                        var modalHtml = `
                            <div class="modal-muestra-crea-publicacion" id="modal-${post.publicacion_id}" style="display:none;">
                                <div class="modal-content-muestra-crea-publicacion">
                                    <span class="close-muestra-crea-publicacion" onclick="cerrarModal(${post.publicacion_id})">&times;</span>
                                    <div class="modal-image-grid-muestra-crea-publicacion">
                                        ${modalImagesHtml}
                                    </div>
                                </div>
                            </div>
                        `;

                        postDisplayContainer.append(modalHtml);
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




}



function cerrarPublicacion(publicacionId) {
  var access_token = localStorage.getItem('access_token');

  // Enviar solicitud AJAX para actualizar el estado de la publicación
  $.ajax({
      url: '/social_media_publicaciones_borrado_logico_publicaciones', // Asegúrate de que esta URL sea correcta
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
  // Redirigir al usuario a una nueva página que muestra todos los detalles de la publicación
  window.location.href = `/media-muestraPublicacionesEnDpi-mostrar/${publicacionId}`;
}













// Función para obtener el valor de una cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}


var currentLanguage = 'in';

// Obtener el enlace para cambiar el idioma
const languageLink = document.getElementById("languageLink");

// Si no existe la cookie "language", se crea y se establece "in" como idioma
if (!getCookie("language")) {
    document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`; // Validez de 1 año
    currentLanguage = "in";
    localStorage.setItem("language", currentLanguage);
    // Cambiar el texto del enlace según el idioma
    languageLink.textContent = "ENG";  // Cambiar solo a "ENG"
} else {
    // Si ya existe la cookie, obtener el valor y poner el texto de acuerdo a ella
    currentLanguage = getCookie("language");
    localStorage.setItem("language", currentLanguage);
    languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
}





function cambiarIdioma() {
    

document.addEventListener("DOMContentLoaded", function () {
    const languageLink = document.getElementById("languageLink");

    // Función para obtener el valor de una cookie
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Función para actualizar el idioma y mostrarlo
    function updateLanguage() {
        // Leer el idioma desde localStorage o cookies
        let currentLanguage = localStorage.getItem("language") || getCookie("language");

        // Si no hay un idioma configurado, asignar "in" como valor inicial
        if (!currentLanguage) {
            currentLanguage = "in";
        } else {
            // Alternar entre "in" y "es"
            currentLanguage = currentLanguage === "in" ? "es" : "in";
        }

        // Guardar el idioma actualizado en localStorage y cookies
        localStorage.setItem("language", currentLanguage);
        document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`; // Validez de 1 año

        // Actualizar el texto del enlace
        languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";

        alert(`Idioma actualizado: ${currentLanguage}`);
    }

    // Establecer el idioma inicial y el texto del enlace
    (function setInitialLanguage() {
        const currentLanguage = localStorage.getItem("language") || getCookie("language") || "in";
        languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
    })();

    // Agregar el evento para alternar el idioma
    languageLink.addEventListener("click", function (event) {
        event.preventDefault(); // Evitar la recarga de la página
        updateLanguage();
       
        cargarAmbitos();
        cargarAmbitosCarrusel(); // Llamar a la función cuando el DOM esté listo
    });
});

}

























