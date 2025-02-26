document.addEventListener("DOMContentLoaded", function() {
    const video = document.getElementById('main-video');

    if (video) {
        video.addEventListener('click', function(event) {
            const rect = video.getBoundingClientRect();
            const clickX = event.clientX - rect.left;
            const clickY = event.clientY - rect.top;
    
            // Definir el área del centro (20% del ancho y 20% del alto)
            const centerWidth = rect.width * 0.2;
            const centerHeight = rect.height * 0.2;
            const centerX = rect.width / 2 - centerWidth / 2;
            const centerY = rect.height / 2 - centerHeight / 2;
    
            // Verificar si el clic está dentro del área central
            if (clickX >= centerX && clickX <= centerX + centerWidth &&
                clickY >= centerY && clickY <= centerY + centerHeight) {
                // Si el clic está en el centro, reproducir o pausar el video
                if (video.paused) {
                    video.play();
                } else {
                    video.pause();
                }
            } else {
                // Si el clic está fuera del centro, ejecutar cargarDatosPublicacion()
                cargarDatosPublicacion();
            }
        });
    } else {
        console.warn("El elemento video no se encuentra disponible.");
    }
});








// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}


function cargarDatosPublicacion() {

    // Redirigir a la URL construida con los parámetros
    window.location.href = `/media-muestraPublicacionesEnAmbitos?publicacion_id=${publicacionId}&user_id=${userId}&ambito=${ambito}&layout=${layout}`;
}

function mostrarPublicacionesEnAmbitos(publicacionId, userId, ambito, layout) {
     // Mostrar el splash de espera
    var splash = document.querySelector('.splashCarga');

    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }

    
    
    var galeriaURL1 = '/media-muestraPublicacionesEnAmbitos-mostrar/';
    var access_token = localStorage.getItem('access_token');
    let lenguaje = localStorage.getItem('language') || 'es'; // Por defecto 'es' si no está definido

    $.ajax({
        type: 'POST',
        url: galeriaURL1,
        data: JSON.stringify({
            publicacion_id: publicacionId,
            user_id: userId,
            ambito: ambito,
            layout: layout,
            lenguaje: lenguaje
        }),
        contentType: 'application/json', // Indica que se envía un JSON al backend
        dataType: 'json', // Asegúrate de que el backend devuelva un JSON
        headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado

        success: function (response) {
           if(!localStorage.getItem('dominio')){
              localStorage.setItem('dominio', ambito);
               
           }
            splash.style.display = 'none'; // Ocultar el splash al terminar
            if (Array.isArray(response)) {
                var postDisplayContainer = $('.home-muestra-publicaciones-en-ambitos-personales-centrales');
                postDisplayContainer.empty();

                response.forEach(function(post) {
                    if ((post.imagenes && post.imagenes.length > 0) || (post.videos && post.videos.length > 0)) {
                        var mediaHtml = '';
                
                        // Primero, mostrar la primera imagen si hay imágenes
                        if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                            var firstImageUrl = post.imagenes[0].imagen 
                                ? `data:${post.imagenes[0].mimetype};base64,${post.imagenes[0].imagen}`
                                : post.imagenes[0].filepath;
                
                            mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" 
                                onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')"
                                style="cursor: pointer;" class="first-image">`;
                        }
                
                        // Luego, si también hay videos, mostrar el primero después de la imagen
                        if (Array.isArray(post.videos) && post.videos.length > 0) {
                            var firstVideoUrl = post.videos[0].filepath;
                
                            mediaHtml += `
                                <video controls onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                    <source src="${firstVideoUrl}" type="video/mp4">                                           
                                    Tu navegador no soporta la reproducción de videos.
                                </video>
                            `;
                        }
                
                        // Modal solo si hay más de una imagen
                        if (Array.isArray(post.imagenes) && post.imagenes.length > 1) {
                            var modalImagesHtml = '';
                            post.imagenes.forEach(function(image, index) {
                                if (index > 0) { // No incluir la primera imagen porque ya se mostró
                                    modalImagesHtml += `<img src="${image.filepath}" alt="Imagen de la publicación" 
                                        class="imagen-muestra-publicacion-en-ambito">`;
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
                            <div class="card-publicacion-en-ambitos-personales" id="card-${post.publicacion_id}" style="margin-top: 100px;">
                                <div class="card-body-en-ambitos-personales">
                                    <h5 class="card-title-en-ambitos-personales">${post.titulo}</h5>
                                    <h6 class="card-title-en-ambitos-personales">user_id: ${post.user_id}</h6>
                                    <div class="card-media-grid-publicacion-en-ambitos-personales">
                                        ${mediaHtml}
                                    </div>
                                    <p class="card-date-en-ambitos-personales">${formatDate(post.fecha_creacion)}</p>
                                    <p class="card-text-en-ambitos-personales text-truncated-en-ambitos-personales" id="postText-${post.publicacion_id}">${post.texto}</p>
                                    <a href="#" class="btn-ver-mas" onclick="toggleTexto(${post.publicacion_id}); return false;">Ver más</a>
                                    ${post.botonCompra ? `
                                        <button id="btn-comprar-${post.publicacion_id}" style="background-color: #28a745; color: white; font-size: 12px; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s ease;"
                                        onmouseover="this.style.backgroundColor='#218838'" onmouseout="this.style.backgroundColor='#28a745'"
                                        onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                            Agregar
                                        </button>` : ''
                                    }
                                </div>
                            </div>
                        `;
                
                        postDisplayContainer.append(cardHtml);
                 // Desplazar la tarjeta hacia abajo si se ha mostrado una imagen
                 if (post.imagenes.length > 0) {
                    $('#card-' + post.publicacion_id).css('margin-top', '100px');
                }
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

function abrirPublicacionHome(publicacionId, layout) {
    // Redirigir al usuario a una nueva página que muestra todos los detalles de la publicación
    const accessToken = localStorage.getItem('access_token');

    if (!accessToken) {
        alert("Para adquirir este contenido, debe iniciar sesión. Si no es usuario, regístrese.");
        return;
    }
    window.location.href = `/media-muestraPublicacionesEnHome-mostrar/${publicacionId}/${layout}`;
}



