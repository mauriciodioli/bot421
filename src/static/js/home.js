// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}


// Ruta al archivo con la galería de imágenes
var galeriaURL = '/MostrarImages/';
var galeriaURL1 = '/media-publiaciones-mostrar';
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
                    switch (post.estado) {
                        case 'activo':
                            estadoClass = 'estado-activo';
                            estadoTextClass = 'estado-activo';
                            break;
                        case 'inactivo':
                            estadoClass = 'estado-inactivo';
                            estadoTextClass = 'estado-inactivo';
                            break;
                        case 'pendiente':
                            estadoClass = 'estado-pendiente';
                            estadoTextClass = 'estado-pendiente';
                            break;
                        default:
                            estadoClass = '';
                            estadoTextClass = '';
                    }

                    var cardHtml = `
                        <div class="card-publicacion-admin ${estadoClass}" id="card-${post.publicacion_id}" onclick="cambiarEstado(event, ${post.publicacion_id})">
                            <div class="card-body">
                                <h5 class="card-title">${post.titulo}</h5>
                                <p class="card-text-estado ${estadoTextClass}">${post.estado}</p>
                                <p class="card-text">${post.correo_electronico}</p>
                                <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                <p class="card-text">${post.texto}</p>
                                <div class="card-media-grid-publicacion-admin">
                                    ${mediaHtml}
                                </div>
                                <p class="card-text">${post.ambito}</p>
                                <p class="card-text">${post.descripcion}</p>
                                <div class="btn-modificar-eliminar">
                                    <button class="btn-modificar" onclick="modificarPublicacion(${post.publicacion_id})">Modificar</button>
                                    <button class="btn-eliminar" onclick="eliminarPublicacion(${post.publicacion_id})">Eliminar</button>
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

