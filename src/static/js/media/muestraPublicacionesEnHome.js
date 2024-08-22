// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}


// Ruta al archivo con la galería de imágenes
var galeriaURL = '/MostrarImages/';
var galeriaURL1 = '/media-publicaciones-mostrar';
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
                    var baseUrl = window.location.origin;

                    if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                        // Mostrar solo la primera imagen
                        var firstImageUrl = baseUrl + '/' + post.imagenes[0].filepath;
                        mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;

                        // Guardar las demás imágenes para mostrarlas en el modal
                        var modalImagesHtml = '';
                        post.imagenes.forEach(function(image, index) {
                            if (index > 0) { // Saltar la primera imagen
                                var imageUrl = baseUrl + '/' + image.filepath;
                                modalImagesHtml += `<img src="${imageUrl}" alt="Imagen de la publicación" class="imagen-muestra-crea-publicacion">`;
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
                                <button class="btn-close-publicacion" onclick="cerrarPublicacion(${post.publicacion_id})">
                                    <span class="text-white">&times;</span>
                                </button>
                                <h5 class="card-title">${post.titulo}</h5>
                                <p class="card-text">${post.correo_electronico}</p>
                                <div class="card-media-grid-publicacion-admin">
                                    ${mediaHtml}
                                </div>
                                <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                <p class="card-text">${post.ambito}</p>
                                <p class="card-text" id="postText-${post.publicacion_id}" class="text-truncated">${post.texto}</p>
                                <button class="btn-ver-mas" onclick="toggleTexto(${post.publicacion_id})">Ver más</button>
                                <div class="btn-modificar-eliminar">
                                    <button class="btn-modificar" onclick="modificarPublicacion(${post.publicacion_id})">Comunicarse</button>
                                    <button class="btn-eliminar" onclick="eliminarPublicacion(${post.publicacion_id})">Abrir</button>
                                </div>
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
    // Enviar solicitud AJAX para actualizar el estado de la publicación
    $.ajax({
        url: '/ruta/de/tu/servidor/para/eliminar', // Cambia esta URL a la ruta de tu servidor
        type: 'POST',
        data: {
            id: publicacionId,
            estado: 'eliminado', // Actualizar el estado
            usuario: 'ID_DEL_USUARIO' // Cambia esto por el ID del usuario que está realizando la acción
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
    
    if (postText.classList.contains('text-truncated')) {
        postText.classList.remove('text-truncated');
        postText.classList.add('text-expanded');
        button.textContent = 'Ver menos';
    } else {
        postText.classList.remove('text-expanded');
        postText.classList.add('text-truncated');
        button.textContent = 'Ver más';
    }
}
