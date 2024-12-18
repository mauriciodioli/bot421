// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}






function cargarPublicaciones(ambitoParam,layout) {
    
    var access_token = localStorage.getItem('access_token');   
    var ambito = ambitoParam || localStorage.getItem('dominio'); // Usa el parámetro o toma del localStorage
    var galeriaURL = '/media-publicaciones-mostrar-home';
    // Mostrar el splash de espera
    var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }

    $.ajax({
        type: 'POST',
        url: galeriaURL,
        dataType: 'json', // Asegúrate de que el backend devuelva un JSON
        headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
        data: {
            layout: layout,
            ambito: ambito
        },
        success: function (response) {
           
            if (splash) {
                splash.style.display = 'none'; // Ocultar el splash al terminar
            }

            if (Array.isArray(response)) {
                var postDisplayContainer = $('.home-muestra-publicaciones-centrales');
                postDisplayContainer.empty();

                response.forEach(function (post) {
                    if (post.imagenes.length > 0 || post.videos.length > 0) {
                        var mediaHtml = '';

                        // Mostrar la primera imagen
                        if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                            var firstImageUrl = post.imagenes[0].filepath;
                            mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;

                            // Modal para imágenes adicionales
                            var modalImagesHtml = '';
                            post.imagenes.forEach(function (image, index) {
                                if (index > 0) { // Saltar la primera imagen
                                    var imageUrl = image.filepath;
                                    modalImagesHtml += `<img src="${imageUrl}" alt="Imagen de la publicación" class="imagen-muestra-en-ambito-publicacion"> `;
                                }
                            });

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

                        // Tarjeta de publicación
                        var cardHtml = `
                            <div class="card-publicacion-admin" id="card-${post.publicacion_id}">
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
        error: function (xhr, status, error) {
            console.error("Error en la solicitud:", xhr.responseText || error);
        
            // Manejo específico para 401 (Token expirado)
            if (xhr.status === 401) {
                alert("Acceso no autorizado o token expirado. Por favor, inicia sesión nuevamente.");
                // Opcional: redirigir al usuario a la página de inicio de sesión
                // Eliminar el token del localStorage
                localStorage.removeItem('access_token');
                window.location.href = '/'; // Cambia '/login' por tu ruta de inicio de sesión
            }
            
            // Ocultar el splash al terminar
            if (splash) {
                splash.style.display = 'none';
            }
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



/**
 * Toggle the text of a post from truncated to expanded and vice versa.
 * @param {number} postId - The ID of the post to toggle.
 */
function toggleTexto(postId) {
    var postText = document.getElementById(`postText-${postId}`);
    var button = document.querySelector(`#card-${postId} .btn-ver-mas`);
    
    if (button) { // Verifica si el botón existe
        // Si el texto está truncado, elimina la clase 'text-truncated' y agrega 'text-expanded'
        // Si el texto está expandido, elimina la clase 'text-expanded' y agrega 'text-truncated'
        postText.classList.toggle('text-truncated');
        postText.classList.toggle('text-expanded');
        
        // Cambia el texto del botón según sea necesario
        button.textContent = postText.classList.contains('text-truncated') ? 'Ver más' : 'Ver menos';
    } else {
        console.error(`No se encontró el botón para el postId: ${postId}`);
    }
}


function abrirPublicacionHome(publicacionId, layout) {
    // Mostrar el splash de espera
    var splash = document.querySelector('.splashCarga');
    
    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }

    // Redirigir al usuario después de un pequeño retraso
    setTimeout(() => {
        window.location.href = `/media-muestraPublicacionesEnHome-mostrar/${publicacionId}/${layout}`;
    }, 500); // 500 ms de retraso para mostrar el splash
}

