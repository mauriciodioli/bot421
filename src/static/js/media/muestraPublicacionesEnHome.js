// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}


// Ruta al archivo con la galería de imágenes
var galeriaURL = '/MostrarImages/';
var galeriaURL1 = '/media-publicaciones-mostrar-home';
var access_token = localStorage.getItem('access_token');

$.ajax({
    type: 'POST',
    url: galeriaURL1,
    dataType: 'json', // Asegúrate de que el backend devuelva un JSON
    headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
    success: function (response) {
        if (Array.isArray(response)) {
            var postDisplayContainer = $('.home-muestra-publicaciones-centrales');
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
    window.location.href = `/media-muestraPublicacionesEnHome-mostrar/${publicacionId}`;
}

