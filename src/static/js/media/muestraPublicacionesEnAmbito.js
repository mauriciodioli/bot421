// Define la función formatDate




function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}




function mostrarPublicacionesEnAmbitos(publicacionId, userId, ambito, layout) {
    var galeriaURL1 = '/media-muestraPublicacionesEnAmbitos-mostrar';
    var access_token = localStorage.getItem('access_token');
    
    $.ajax({
        type: 'POST',
        url: galeriaURL1,
        data: JSON.stringify({
            publicacion_id: publicacionId,
            user_id: userId,
            ambito: ambito,
            layout: layout
        }),
        contentType: 'application/json', // Indica que se envía un JSON al backend
        dataType: 'json', // Asegúrate de que el backend devuelva un JSON
        headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado

        success: function (response) {
            if (Array.isArray(response)) {
                var postDisplayContainer = $('.home-muestra-publicaciones-en-ambitos-personales-centrales');
                postDisplayContainer.empty();

                response.forEach(function(post) {
                    if (post.imagenes.length > 0 || post.videos.length > 0) {
                        var mediaHtml = '';

                        if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                            var firstImageUrl = post.imagenes[0].filepath;
                            mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id})" style="cursor: pointer;" class="first-image">`;

                            var modalImagesHtml = '';
                            post.imagenes.forEach(function(image, index) {
                                if (index > 0) {
                                    var imageUrl = image.filepath;
                                    modalImagesHtml += `<img src="${imageUrl}" alt="Imagen de la publicación" class="imagen-muestra-publicacion-en-ambito">`;
                                }
                            });

                            var modalHtml = `
                                <div class="modal-muestra-publicacion-en-ambito" id="modal-${post.publicacion_id}" style="display:none;">
                                    <div class="modal-content-muestra-publicacion-en-ambito">
                                        <span class="close-muestra-publicacion-en-ambito" onclick="cerrarModalEnAmbito(${post.publicacion_id})">&times;</span>
                                        <div class="modal-image-grid-muestra-publicacion-en-ambito">
                                            ${modalImagesHtml}
                                        </div>
                                    </div>
                                </div>
                            `;
                            postDisplayContainer.append(modalHtml);
                        }

                        var cardHtml = `
                            <div class="card-publicacion-en-ambitos-personales" id="card-${post.publicacion_id}">
                                <div class="card-body-en-ambitos-personales">
                                    <h5 class="card-title-en-ambitos-personales">${post.titulo}</h5>
                                    <div class="card-media-grid-publicacion-en-ambitos-personales">
                                        ${mediaHtml}
                                    </div>
                                    <p class="card-date-en-ambitos-personales">${formatDate(post.fecha_creacion)}</p>
                                    <p class="card-text-en-ambitos-personales text-truncated-en-ambitos-personales" id="postText-${post.publicacion_id}">${post.texto}</p>
                                    <a href="#" class="btn-ver-mas-en-ambitos-personales" onclick="toggleTexto(${post.publicacion_id}); return false;">Ver más</a>
                                </div>
                            </div>
                        `;
                        
                        postDisplayContainer.append(cardHtml);

                        // Desplazar la tarjeta hacia abajo si se ha mostrado una imagen
                        if (post.imagenes.length > 0) {
                            $('#card-' + post.publicacion_id).css('margin-top', '100px');
                        }
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




function toggleTexto(postId) {
   
    var postText = document.getElementById(`postText-${postId}`);
    var button = document.querySelector(`#card-${postId} .btn-ver-mas-en-ambitos-personales`);
    
    if (postText.classList.contains('text-truncated-en-ambitos-personales')) {
        postText.classList.remove('text-truncated-en-ambitos-personales');
        postText.classList.add('text-expanded-en-ambitos-personales');
        button.textContent = 'Ver menos';
    } else {
        postText.classList.remove('text-expanded-en-ambitos-personales');
        postText.classList.add('text-truncated-en-ambitos-personales');
        button.textContent = 'Ver más';
    }
}

function abrirPublicacionHome(publicacionId) {
    // Redirigir al usuario a una nueva página que muestra todos los detalles de la publicación
   
    window.location.href = `/media-muestraPublicacionesEnHome-mostrar/${publicacionId}`;
}


