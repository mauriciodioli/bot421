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

// Añadir un evento click a cada ítem del menú dropdown
document.querySelectorAll('.dropdown-item').forEach(item => {
  item.addEventListener('click', function (event) {
      event.preventDefault(); // Previene el comportamiento predeterminado del enlace
      var selectedDomain = this.id; // Toma el ID del elemento clickeado como el dominio seleccionado
      
      // Actualizar el valor del input hidden
      document.getElementById('domain').value = selectedDomain;
      
      console.log("Dominio seleccionado:", selectedDomain); // Mostrar el dominio seleccionado en la consola

      // Hacer algo con el valor actualizado (por ejemplo, enviar una solicitud AJAX)
      enviarDominioAJAX(selectedDomain);
  });
});



// Realizar la solicitud AJAX al cargar la página
$(document).ready(function () {
  // Obtener el valor por defecto del input hidden cuando carga la página
    var domain = document.getElementById('domain').value;

    enviarDominioAJAX(domain);
});



// Define la función formatDate
function formatDate(dateString) {
  var options = { year: 'numeric', month: 'long', day: 'numeric' };
  var date = new Date(dateString);
  return date.toLocaleDateString(undefined, options);
}

function enviarDominioAJAX(domain) {


// Ruta al archivo con la galería de imágenes
var galeriaURL = '/MostrarImages/';
var galeriaURL1 = '/media-publicaciones-mostrar-dpi';
var access_token = 'access_dpi_token_usuario_anonimo';

$.ajax({
  type: 'POST',
  url: galeriaURL1,
  dataType: 'json', // Asegúrate de que el backend devuelva un JSON
  headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
  data: { ambitos: domain }, // Enviar el dominio como parte de los datos
  success: function (response) {
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
                console.log('Publicación sin contenido:', post.publicacion_id);
            }
        });
    } else {
        console.error("La respuesta no es un array. Recibido:", response);
    }
},
error: function () {
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


