document.addEventListener('DOMContentLoaded', function() {
    muestraGaleriadePublicaciones();

 // Agregar manejador de eventos para el formulario
 var form = document.getElementById('modificarPostForm_modificaPublicacion');
 form.addEventListener('submit', function(event) {
   event.preventDefault(); // Prevenir el envío por defecto del formulario
   
   // Enviar los datos del formulario por AJAX
   enviarDatosFormulario();
 });

   
  });
  
  
  /**
   * Carga las publicaciones en el contenedor
   * #postDisplayContainer y las muestra en tarjetas.
   * Las publicaciones se obtienen haciendo una petición
   * AJAX a la URL '/media-publicaciones-mostrar'.
   * Se envía el token de acceso en el encabezado
   * 'Authorization'.
   */
  function muestraGaleriadePublicaciones() {
    var correo_electronico = localStorage.getItem('correo_electronico');
    var roll = localStorage.getItem('roll');
    var access_token = localStorage.getItem('access_token');
  
    if (!access_token) {
      alert("No se ha encontrado el token de acceso.");
      return;
    }
  
    var formData = new FormData();
    formData.append('roll', roll);
    formData.append('correo_electronico', correo_electronico);
  
    $.ajax({
      url: '/media-publicaciones-mostrar',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        'Authorization': 'Bearer ' + access_token
      },success: function(response) {
        if (Array.isArray(response)) {
            var postAccordion = $('#postAccordion');
            postAccordion.empty();
    
            // Crear un objeto para almacenar las publicaciones por ámbito
            var postsByAmbito = {};
            // Iterar sobre las publicaciones para organizarlas por ámbito
            response.forEach(function(post) {
                if (!postsByAmbito[post.ambito]) {
                    postsByAmbito[post.ambito] = [];
                }
                postsByAmbito[post.ambito].push(post);
            });
    
            // Crear secciones del acordeón para cada ámbito
            Object.keys(postsByAmbito).forEach(function(ambito, index) {
                var ambitoId = 'ambito-' + index; // ID único para cada ámbito
                var publicaciones = postsByAmbito[ambito];
    
                var accordionItemHtml = `
                    <div class="accordion-item">
                        <h2 class="accordion-header" id="heading-${ambitoId}">
                            <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${ambitoId}" aria-expanded="true" aria-controls="collapse-${ambitoId}">
                                ${ambito}
                            </button>
                        </h2>
                        <div id="collapse-${ambitoId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" aria-labelledby="heading-${ambitoId}" data-bs-parent="#postAccordion">
                            <div class="accordion-body">
                                <div id="accordion-content-${ambitoId}" class="accordion-content">
                                    <div class="card-grid-publicaciones"> <!-- Aquí se aplica la clase de grilla -->
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
    
                postAccordion.append(accordionItemHtml);
    
                var accordionContent = $(`#accordion-content-${ambitoId} .card-grid-publicaciones`);
    
                // Agregar publicaciones al acordeón correspondiente
                publicaciones.forEach(function(post) {
                    var mediaHtml = '';
                    var baseUrl = window.location.origin;
    
                    if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                        var firstImageUrl = baseUrl + '/' + post.imagenes[0].filepath;
                        mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
    
                        var modalImagesHtml = '';
                        post.imagenes.forEach(function(image) {
                            var imageUrl = baseUrl + '/' + image.filepath;
                            modalImagesHtml += `
                                <div id="image-container-modal-publicacion-crear-publicacion-${image.id}" class="image-container-modal-publicacion-crear-publicacion">
                                    <img src="${imageUrl}" alt="Imagen de la publicación" onclick="abrirImagenEnGrande('${imageUrl}')">
                                    <button class="close-button-media_imagenes" onclick="removeImageFromModal(${post.publicacion_id}, ${image.id}, '${image.title}', '${image.size}', '${image.filepath}')">X</button>
                                </div>
                                  <!-- Container to display selected images and videos -->
                                  <input type="file" id="imagen-media_imagenes" name="mediaFile_creaPublicacion" accept="image/*,video/*" multiple onchange="previewSelectedMedia()">
                                  <div id="mediaContainer_creaPublicacion" class="media-container_creaPublicacion"></div>
                                   

                            `;
                        });
    
                        var modalHtml = `
                            <div class="mostrar-imagenes-en-modal-publicacion-crear-publicacion" id="modal-${post.publicacion_id}" style="display:none;">
                                <div class="modal-content-mostrar-imagenes-en-modal-publicacion-crear-publicacion">
                                    <span class="close" onclick="cerrarModal(${post.publicacion_id})">&times;</span>
                                    <div class="modal-image-grid">
                                        ${modalImagesHtml}
                                    </div>
                                    <div class="modal-buttons-mostrar-imagenes-en-modal-publicacion-crear-publicacion">
                                        <label for="imagen-media_imagenes" class="custom-file-upload-media_imagenes">
                                            <input type="file" name="imagen" id="imagen-media_imagenes" accept="image/*" onchange="agregarImagen(${post.publicacion_id})">
                                            <i class="fas fa-folder"></i> Agregar Imagen o viedeo
                                        </label>
                                     
                                    </div>
                                </div>
                            </div>
                        `;
    
                        accordionContent.append(modalHtml);
                    }
    
                    var cardHtml = `
                        <div class="card-publicacion-admin" id="card-${post.publicacion_id}" onclick="cambiarEstado(event, ${post.publicacion_id})">
                            <div class="card-body">
                                <h5 class="card-title">${post.titulo}</h5>
                                <p class="card-text-estado">${post.estado}</p>
                                <p class="card-text-email">${post.correo_electronico}</p>
                                <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                <p class="card-text">${post.texto}</p>
                                <div class="card-media-grid-publicacion-admin">
                                    ${mediaHtml}
                                </div>
                                <p class="card-text-ambito">${post.ambito}</p>
                                <p class="card-text-descripcion">${post.descripcion}</p>
                                <div class="btn-modificar-eliminar">
                                    <button class="btn-modificar" onclick="modificarPublicacion(${post.publicacion_id})">Modificar</button>
                                    <button class="btn-eliminar" onclick="eliminarPublicacion(${post.publicacion_id})">Eliminar</button>
                                </div>
                            </div>
                        </div>
                    `;
    
                    accordionContent.append(cardHtml);
                });
            });
        } else {
            console.log('Respuesta no válida');
        }
    },
    
    
      error: function(xhr, status, error) {
        alert("Error al cargar las publicaciones. Inténtalo de nuevo.");
      }
    });
  }
  



  function previewSelectedMedia() {
    var fileInput = document.getElementById('imagen-media_imagenes');
    var mediaContainer = document.getElementById('mediaContainer_creaPublicacion');
    mediaContainer.innerHTML = ''; // Limpiar contenido previo
  
    var files = fileInput.files;
  
    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();
  
        reader.onload = (function(file) {
            return function(e) {
                var mediaElementWrapper = document.createElement('div');
                mediaElementWrapper.className = 'media-element-wrapper';
  
                var mediaElement;
  
                if (file.type.startsWith('image/')) {
                    mediaElement = document.createElement('img');
                    mediaElement.src = e.target.result;
                    mediaElement.className = 'media-preview-image';
                } else if (file.type.startsWith('video/')) {
                    mediaElement = document.createElement('video');
                    mediaElement.src = e.target.result;
                    mediaElement.controls = true;
                    mediaElement.className = 'media-preview-video';
                }
  
                if (mediaElement) {
                    // Crear botón de cierre
                    var closeButton = document.createElement('button');
                    closeButton.className = 'close-button-media_imagenes';
                    closeButton.textContent = 'X';
                    closeButton.onclick = function() {
                        mediaContainer.removeChild(mediaElementWrapper);
                    };
  
                    // Añadir media y botón al contenedor
                    mediaElementWrapper.appendChild(mediaElement);
                    mediaElementWrapper.appendChild(closeButton);
                    mediaContainer.appendChild(mediaElementWrapper);
                }
            };
        })(file);
  
        reader.readAsDataURL(file);
    }
  }


// Función para abrir la imagen en grande
function abrirImagenEnGrande(imageUrl) {
  // Crear el modal si no existe
  if ($('#modalImagenGrande').length === 0) {
      $('body').append(`
          <div id="modalImagenGrande" class="modal-imagen-grande" style="display:none;">
              <div class="modal-content-imagen-grande">
                  <span class="close" onclick="cerrarModalImagenGrande()">&times;</span>
                  <img id="imagenEnGrande" src="" alt="Imagen en grande">
              </div>
          </div>
      `);
  }

  // Mostrar la imagen en el modal
  $('#imagenEnGrande').attr('src', imageUrl);
  $('#modalImagenGrande').show();
}

// Función para cerrar el modal de imagen en grande
function cerrarModalImagenGrande() {
  $('#modalImagenGrande').hide();
}













  /**
   * Cierra un modal por su id
   * @param {string} modalId - Identificador del modal a cerrar
   */
  function cerrarModalModificacion(modalId) {
    // Obtener el modal por su id
    var modal = document.getElementById(modalId);

    // Si se encontró el modal, ocultarlo
    if (modal) {
      modal.style.display = 'none'; // Ocultar el modal
    }
  }


  /**
   * Muestra el modal para modificar una publicación
   * @param {number} id - Identificador de la publicación a modificar
   */
  function modificarPublicacion(id) {
    // Mostrar el modal
    var modal = document.getElementById('modificarPostModal_modificaPublicacion');
    modal.style.display = 'block'; // Mostrar el modal

    // Opcional: Puedes cargar los datos de la publicación en el modal
    cargarDatosPublicacion(id);
  }


  /**
   * Carga los datos de una publicación en el modal para editarla.
   * @param {number} id - Identificador de la publicación a editar
   */
  function cargarDatosPublicacion(id) {
    // Obtener la información del post desde el DOM si ya está cargada
    var postCard = document.getElementById(`card-${id}`);
    if (postCard) {
      // Obtener los datos de la publicación
      var id_publicacion = id;
      var titulo = postCard.querySelector('.card-title').textContent;
      var texto = postCard.querySelector('.card-text').textContent;
      var descripcion = postCard.querySelector('.card-text-descripcion').textContent;
      var estado = postCard.querySelector('.card-text-estado').textContent;
      var ambito = postCard.querySelector('.card-text-ambito').textContent;

      // Cargar los datos en el modal
      document.getElementById('postId_modificaPublicacion').value = id_publicacion;
      document.getElementById('postTitle_modificaPublicacion').value = titulo;
      document.getElementById('postText_modificaPublicacion').value = texto;
      document.getElementById('postDescription_modificaPublicacion').value = descripcion;
      document.getElementById('postEstado_modificaPublicacion').value = estado;
      document.getElementById('postAmbito_modificaPublicacion').value = ambito;

      // Limpiar el contenedor de medios y agregar la imagen
      var mediaContainer = document.getElementById('mediaContainer_modificaPublicacion');
      // Limpiar el contenedor de medios
      mediaContainer.innerHTML = ''; // Limpiar el contenedor antes de agregar nuevos elementos
    }
  }
  



 
  
 
 
    

  function enviarDatosFormulario() {
  var access_token = localStorage.getItem('access_token');
  if (!access_token) {
    alert("No se ha encontrado el token de acceso.");
    return;
  }

  var formData = new FormData(document.getElementById('modificarPostForm_modificaPublicacion'));
  var postId = document.getElementById('postId_modificaPublicacion').value;
  formData.append('postId_modificaPublicacion', postId);

  $.ajax({
    url: '/social_media_publicaciones_modificar_publicaciones', // Cambia esta URL a la ruta correcta en tu servidor
    type: 'POST',
    data: formData,
    contentType: false, // No establecer el Content-Type
    processData: false, // No procesar los datos
    headers: {
      'Authorization': 'Bearer ' + access_token
    },
    success: function(response) {
      alert('Publicación modificada con éxito!');
      actualizarTarjeta(postId); // Actualiza la tarjeta con los nuevos datos
      cerrarModalModificacion('modificarPostModal_modificaPublicacion'); // Cerrar el modal
    },
    error: function(xhr, status, error) {
      alert('Error al modificar la publicación. Inténtalo de nuevo.');
      console.error('Error:', error); // Imprime el error en la consola para más detalles
    }
  });
}

function actualizarTarjeta(postId) {
  // Obtener los nuevos datos del servidor (opcional, si necesitas obtener datos actualizados del servidor)
  // o actualiza directamente la tarjeta con los datos conocidos

  var postCard = document.getElementById(`card-${postId}`);
  if (postCard) {
    // Obtener los datos del formulario (puedes usar variables globales si lo prefieres)
    var titulo = document.getElementById('postTitle_modificaPublicacion').value;
    var texto = document.getElementById('postText_modificaPublicacion').value;
    var descripcion = document.getElementById('postDescription_modificaPublicacion').value;
    var estado = document.getElementById('postEstado_modificaPublicacion').value;
    var ambito = document.getElementById('postAmbito_modificaPublicacion').value;

    // Actualizar los datos en la tarjeta
    postCard.querySelector('.card-title').textContent = titulo;
    postCard.querySelector('.card-text-estado').textContent = estado;
    postCard.querySelector('.card-text-email').textContent = ''; // O actualiza según sea necesario
    postCard.querySelector('.card-date').textContent = ''; // O actualiza según sea necesario
    postCard.querySelector('.card-text').textContent = texto;
   // postCard.querySelector('.card-media-grid-publicacion-admin').innerHTML = ''; // Actualiza el contenido de medios si es necesario
    postCard.querySelector('.card-text-ambito').textContent = ambito;
    postCard.querySelector('.card-text-descripcion').textContent = descripcion;
  }
}

  







  
 
  
  function abrirModal(id) {
    $('#modal-' + id).show();
  }
  
  function cerrarModal(id) {
    $('#modal-' + id).hide();
  }
  
  function formatDate(dateString) {
    const date = new Date(dateString);
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    
    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
  }
  
  function cambiarEstado(event, id) {
    // Evitar el cambio de estado si el clic fue en una imagen
    if (event.target.tagName.toLowerCase() === 'img') {
      return;
    }
  
    var card = document.getElementById('card-' + id);
    var estadoP = card.querySelector('.card-text-estado');
  
    switch (estadoP.textContent.trim()) {
      case 'activo':
        estadoP.textContent = 'inactivo';
        card.classList.remove('estado-activo');
        card.classList.add('estado-inactivo');
        break;
      case 'inactivo':
        estadoP.textContent = 'pendiente';
        card.classList.remove('estado-inactivo');
        card.classList.add('estado-pendiente');
        break;
      case 'pendiente':
        estadoP.textContent = 'activo';
        card.classList.remove('estado-pendiente');
        card.classList.add('estado-activo');
        break;
      default:
        estadoP.textContent = '';
        card.classList.add('estado-activo');
    }
  
  
  
  
    // Obtener el estado actual
    var estadoActual = estadoP.textContent.trim();
    
    // Determinar el próximo estado
    var nuevoEstado;
    switch (estadoActual) {
        case 'activo':
            nuevoEstado = 'inactivo';
            break;
        case 'inactivo':
            nuevoEstado = 'pendiente';
            break;
        case 'pendiente':
            nuevoEstado = 'activo';
            break;
        default:
            nuevoEstado = 'activo'; // Estado por defecto
    }
    
    // Actualizar el texto y la clase CSS
    estadoP.textContent = nuevoEstado;
    card.classList.remove('estado-activo', 'estado-inactivo', 'estado-pendiente');
    estadoP.classList.remove('estado-activo', 'estado-inactivo', 'estado-pendiente');
    
    switch (nuevoEstado) {
        case 'activo':
            card.classList.add('estado-activo');
            estadoP.classList.add('estado-activo');
            break;
        case 'inactivo':
            card.classList.add('estado-inactivo');
            estadoP.classList.add('estado-inactivo');
            break;
        case 'pendiente':
            card.classList.add('estado-pendiente');
            estadoP.classList.add('estado-pendiente');
            break;
    }

    //Aquí podrías enviar el nuevo estado al servidor si es necesario
    $.post('/media-publicaciones-camiar-estado', { id: id, nuevoEstado: nuevoEstado });
}
  



function eliminarPublicacion(id) {
  alert('Eliminar publicación con ID: ' + id);
  eliminarPublicacion(id)
}

function eliminarPublicacion(id) {
    var confirmDelete = confirm('¿Estás seguro de que quieres eliminar esta publicación?');
    if (!confirmDelete) return;

    var correo_electronico = localStorage.getItem('correo_electronico');
    var access_token = localStorage.getItem('access_token');

    if (!access_token) {
        alert("No se ha encontrado el token de acceso.");
        return;
    }

    var formData = new FormData();
    formData.append('publicacion_id', id);
    formData.append('correo_electronico', correo_electronico);

    $.ajax({
        url: '/social_imagenes_eliminar_publicacion',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'Authorization': 'Bearer ' + access_token
        },
        success: function(response) {
            if (response.success) {
                alert('Publicación eliminada exitosamente.');
                $('#card-' + id).remove(); // Eliminar la tarjeta de la interfaz
            } else {
                alert('Error al eliminar la publicación: ' + response.error);
            }
        },
        error: function(xhr, status, error) {
            alert("Error al eliminar la publicación. Inténtalo de nuevo.");
        }
    });
}






/*********************************************************************/
/*********************************************************************/
/********************Agrega imagen o video****************************/
/*********************************************************************/
/*********************************************************************/
function agregarImagen(postId) { 
    // Obtener los elementos con IDs específicos de la publicación
    var fileInput = document.getElementById('imagen-media_imagenes-' + postId);
    var mediaContainer = document.getElementById('mediaContainer_creaPublicacion-' + postId);
    var uploadButton = document.getElementById('open-popup-media_imagenes-' + postId);

    var files = fileInput.files;

    // Limpiar contenido previo en el contenedor
    mediaContainer.innerHTML = '';

    for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();

        reader.onload = (function(file) {
            return function(e) {
                var mediaElement;

                if (file.type.startsWith('image/')) {
                    // Si el archivo es una imagen
                    mediaElement = document.createElement('img');
                    mediaElement.src = e.target.result;
                    mediaElement.style.maxWidth = '100%'; // Ajustar el tamaño si es necesario
                } else if (file.type.startsWith('video/')) {
                    // Si el archivo es un video
                    mediaElement = document.createElement('video');
                    mediaElement.src = e.target.result;
                    mediaElement.controls = true;
                    mediaElement.style.maxWidth = '100%'; // Ajustar el tamaño si es necesario
                }

                if (mediaElement) {
                    mediaContainer.appendChild(mediaElement);
                }
            };
        })(file);

        reader.readAsDataURL(file);
    }

    // Control de estado del botón de subir
    uploadButton.disabled = files.length === 0;

    // Mostrar/ocultar el botón de cerrar previsualización
    var closeButton = document.querySelector('.close-button-carga_publicaciones-' + postId);
    closeButton.style.display = files.length > 0 ? 'block' : 'none';
}




function agregarVideo(postId) {
  window.location.href = `/subirVideo/?layout=layoutConexBroker&postId=${postId}`; 
  console.log('Agregar video para la publicación con ID:', postId);
}






  
  
  












function fetchPosts() {  
    const sortByElement = document.getElementById('sort-by');
    if (!sortByElement) {
        console.error('El elemento con id "sort-by" no se encuentra en el DOM.');
        return;
    }
    const sortBy = sortByElement.value;
    fetch(`/api/posts?sort_by=${sortBy}`)
        .then(response => response.json())
        .then(posts => {
            const postsContainer = document.getElementById('posts');
            postsContainer.innerHTML = '';
            posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'post';
                postElement.innerHTML = `
                    <div class="post-header">
                        <img src="https://via.placeholder.com/40" alt="User Image">
                        <strong>${post.user}</strong>
                        <span>${post.timestamp}</span>
                    </div>
                    <div class="post-body">
                        <p>${post.content}</p>
                        ${post.media_url ? `<video controls src="${post.media_url}"></video>` : ''}
                    </div>
                    <div class="post-footer">
                        <div class="views">Views: ${post.views}</div>
                        <div class="actions">
                            <button class="action">Comment</button>
                            <button class="action">Share</button>
                            <button class="action">Forward</button>
                        </div>
                    </div>
                `;
                postsContainer.appendChild(postElement);
            });
        })
        .catch(error => console.error('Error fetching posts:', error));
}

function createPost() {
    const user = document.getElementById('user').value;
    const content = document.getElementById('content').value;
    const media_url = document.getElementById('media_url').value;

    if (user && content) {
        fetch('/api/posts', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user, content, media_url })
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('user').value = '';
            document.getElementById('content').value = '';
            document.getElementById('media_url').value = '';
            fetchPosts();
        });
    } else {
        alert('Please enter your name and content');
    }
}




















  function eliminarImagen(imageName) {
    // Mostrar un cuadro de confirmación antes de proceder
    var confirmarEliminacion = confirm('¿Estás seguro de que deseas eliminar esta imagen?');

    if (confirmarEliminacion) {
      var accessToken = localStorage.getItem('access_token');
      var randomNumber = Math.round(Math.random() * 1000000);

      $.ajax({
        url: '/eliminarImagen',
        type: 'POST',
        data: {
          randomNumber: randomNumber,
          imageName: imageName,
          // Otros datos si es necesario
        },
        headers: {
          'Authorization': 'Bearer ' + accessToken
        },
        success: function(response) {
          console.log('Imagen eliminada con éxito:', response);
          $('#result').html('Imagen eliminada con éxito. Respuesta del servidor: ' + response);

          // Puedes realizar otras acciones después de eliminar la imagen, como actualizar la interfaz de usuario.
        },
        error: function(error) {
          $('#result').html('Error al eliminar la imagen. Detalles: ' + JSON.stringify(error));
        }
      });
    } else {
      // El usuario canceló la eliminación
      console.log('Eliminación cancelada por el usuario.');
    }
  }

  function cerrarTarjeta(card) {
    card.style.display = 'none';
  }










 
















                         
  /**
   * Elimina una imagen de una publicación.
   * @param {number} id - ID de la publicación.
   * @param {number} index_imagen - Índice de la imagen en la publicación.
   * @param {string} title - Título de la imagen.
   * @param {number} size - Tamaño de la imagen en bytes.
   * @param {string} filepath - Ruta de la imagen en el servidor.
   */
  function removeImageFromModal(id, index_imagen, title, size, filepath) {
    // Preguntar al usuario si está seguro de eliminar la imagen
    var confirmDelete = confirm('¿Estás seguro de que quieres eliminar esta imagen?');
    if (!confirmDelete) return;

    // Obtener el correo electrónico del usuario y el token de acceso
    var correo_electronico = localStorage.getItem('correo_electronico');
    var access_token = localStorage.getItem('access_token');

    // Verificar si el token de acceso existe
    if (!access_token) {
      alert("No se ha encontrado el token de acceso.");
      return;
    }

    // Crear el formulario con los datos de la imagen a eliminar
    var formData = new FormData();
    formData.append('publicacion_id', id);
    formData.append('id_imagen', index_imagen);
    formData.append('nombre_imagen', title);
    formData.append('size_imagen', size);
    formData.append('filepath_imagen', filepath);
    formData.append('correo_electronico', correo_electronico);

    // Realizar la petición AJAX para eliminar la imagen
    $.ajax({
      url: '/social_imagenes_eliminar_Imagenes_Publicaciones',
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      headers: {
        'Authorization': 'Bearer ' + access_token
      },
      success: function(response) {
        // Verificar si la eliminación fue exitosa
        if (response.success) {              
          // Eliminar la tarjeta de la interfaz
          $('#image-container-modal-publicacion-crear-publicacion-' + index_imagen).remove();
        } else {
          // Mostrar un mensaje de error
          alert('Error al eliminar la imagen: ' + response.error);
        }
      },
      error: function(xhr, status, error) {
        // Mostrar un mensaje de error
        alert("Error al eliminar la imagen. Inténtalo de nuevo.");
      }
    });
  }





