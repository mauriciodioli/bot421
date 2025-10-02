// === Esperar a que embed.js esté listo (robusto) ===
window.ensureEmbedReady = window.ensureEmbedReady || function () {
  return new Promise((resolve) => {
    
    if (typeof window.initEmbedPopups === 'function') return resolve();
    const t0 = Date.now();
    (function check () {
      if (typeof window.initEmbedPopups === 'function') return resolve();
      // evita loops infinitos: 10s timeout
      if (Date.now() - t0 > 10000) { console.warn('embed.js no apareció'); return resolve(); }
      setTimeout(check, 50);
    })();
  });
};





// Define la función formatDate
function formatDate(dateString) {
    var options = { year: 'numeric', month: 'long', day: 'numeric' };
    var date = new Date(dateString);
    return date.toLocaleDateString(undefined, options);
}



function cargarPublicaciones(ambitoParam, layout) {
  
    var access_token = localStorage.getItem('access_token');   
    var ambito = ambitoParam || localStorage.getItem('dominio'); // Usa el parámetro o toma del localStorage
    
    let ambito_actual = "<a style='text-decoration:none; color:orange;'>" + ambito + "</a>";
    
    var codigoPostal = localStorage.getItem('codigoPostal'); // Obtener el código postal de localStorage
    var categoria = localStorage.getItem('categoria'); // Obtener la categoría de localStorage
    if (!categoria) {
        categoria = '1';
    }
    // Si no existe el código postal, solicitarlo
    if (!codigoPostal) {
        codigoPostal = prompt("Por favor, ingresa tu código postal:");

        if (codigoPostal) {
            localStorage.setItem('codigoPostal', codigoPostal); // Guardar en localStorage
        } else {
            codigoPostal = '1';
            alert("El código postal es obligatorio para continuar.");
            return; // Detener la ejecución si no se proporciona
        }
    }

    // Verificar si el elemento con ID "ambito_actual" existe antes de asignarlo
    var ambitoElement = document.getElementById("ambito_actual");
    if (ambitoElement) {
        ambitoElement.innerHTML = ambito_actual;
    }

    var galeriaURL = '/media-publicaciones-mostrar-home/';
    
    // Mostrar el splash de espera
    var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }

    let lenguaje = localStorage.getItem('language') || 'es'; // Por defecto 'es' si no está definido

    // Realizar la petición AJAX
    $.ajax({
        type: 'POST',
        url: galeriaURL,
        dataType: 'json', // Asegúrate de que el backend devuelva un JSON
        headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
        data: {
            layout: layout,
            ambito: ambito,
            lenguaje: lenguaje,
            categoria: categoria,
            codigoPostal: codigoPostal
        },
        success: function (response) {

            if (splash) {
                splash.style.display = 'none'; // Ocultar el splash al terminar
            }

            if (Array.isArray(response)) {
                var postDisplayContainer = $('.home-muestra-publicaciones-centrales');
                postDisplayContainer.empty();
          
                let publicacionesValidas = 0;
                    // === Intercalado: config + anchor HTML (antes del forEach) ===
                    const popupCada = 1; // cada cuántas cards reales metés un popup
                    let cardsRenderizadas = 0;

                    const paramsPopup = {
                    dominio:  'Technologia',
                    categoria:'wearables',
                    lang:     'pl',
                    cp:       localStorage.getItem('codigoPostal') || '60-001',
                    width:    168,
                    height:   300,
                    color:    '#7CFC00'
                    };

                    const anchorHTML = `
                    <div class="card-publicacion-admin popup-fake-card">
                        <div class="dpia-spot"
                        data-dominio="${paramsPopup.dominio}"
                        data-categoria="${paramsPopup.categoria}"
                        data-lang="${paramsPopup.lang}"
                        data-cp="${paramsPopup.cp}"
                        data-width="${paramsPopup.width}"
                        data-height="${paramsPopup.height}"
                        data-placeholder-color="${paramsPopup.color}">
                        </div>
                    </div>`;
                var categoria_id = null; // Variable para almacenar la categoría actual                
                response.forEach(function (post) {
                     publicacionesValidas++;
              
                    const imgs = Array.isArray(post.imagenes) ? post.imagenes : [];
                    const vids = Array.isArray(post.videos)   ? post.videos   : [];
                    if ((imgs.length > 0) || (vids.length > 0)) {
                     
                        var mediaHtml = '';


                       
                        if (categoria_id != post.categoria_id) {
                            categoria_id = post.categoria_id;
                        } 

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
                                        <video controls onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                            <source src="${firstVideoUrl}" type="video/mp4">                                           
                                            Tu navegador no soporta la reproducción de videos.
                                        </video>
                                    `;

                            } else {
                                // Si no hay ni imágenes ni videos, mostrar un mensaje o imagen por defecto
                                mediaHtml += `<p>No hay contenido multimedia disponible.</p>`;
                            }








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
                     
                      //const { precio, descripcion } = extraerPrecioYDescripcion(post.texto);
                        const lang    = window.currentLang || 'es';
                        const vid     = localStorage.getItem('visitor_id');

                        const user_id = localStorage.getItem('usuario_id') || '';

                        const btnComprarAttrs = `
                        href="#"
                        class="btn btn-danger mt-2"
                        rel="nofollow sponsored"
                        data-ali-redirect="1"
                        data-pub-id="${post.publicacion_id}"
                        data-vid="${vid}"
                        data-user-id="${user_id}"
                        data-lang="${lang}"
                        `;

                      // Tarjeta
                        const comprarTxt = (translations[lang] && translations[lang].comprarAli) || 'Comprar';
                        const verMasTxt  = (translations[lang] && translations[lang].verMas) || 'Ver más';

                        // Tarjeta de publicación
                        var cardHtml = `
                                <div class="card-publicacion-admin" id="card-${post.publicacion_id}">
                                    <div class="card-body">

                                        <!-- Botón cerrar -->
                                        <a class="btn-close-publicacion" onclick="cerrarPublicacion(${post.publicacion_id})">
                                            <span class="text-white">&times;</span>
                                        </a>

                                        <!-- BADGES: categoría + descuento -->
                                        <div class="card-badges">
                                            <div class="categoria-badge">${post.categoriaNombre}</div>
                                            ${post.descuento ? `<div class="descuento-badge">${post.descuento}</div>` : ''}
                                        </div>

                                        <!-- Imagen -->
                                        <div class="card-media-grid-publicacion-en-ambito" onclick="abrirPublicacionHome(${post.publicacion_id}, 'layout')" style="cursor: pointer;">
                                            ${mediaHtml}
                                        </div>

                                        <!-- Título -->
                                        <h5 class="card-title">${post.titulo}</h5>

                                        <!-- Estrellas con cantidad -->
                                        <div class="estrellas">
                                            ${generarEstrellas(post.rating || 4)} <span class="text-muted" style="font-size: 0.9rem;">(${post.reviews || 1})</span>
                                        </div>

                                        <!-- Precios -->
                                        ${post.precio_original ? `<p class="precio-original text-muted" style="text-decoration: line-through; font-size: 0.95rem;"> ${post.precio_original}</p>` : ''}
                                        ${post.precio ? `<p class="card-precio text-success fw-bold" style="font-size: 1.2rem;">${post.simbolo} ${post.precio}</p>` : ''}

                                        <!-- Descripción -->
                                        <p class="card-text text-truncated" id="postText-${post.publicacion_id}">${post.texto}</p>

                                        <!-- Fecha -->
                                        <p class="card-date">${formatDate(post.fecha_creacion)}</p>

                                        <!-- Usuario -->
                                        <p class="card-footer-publicacion">Publicado por: Usuario ${post.user_id}</p>

                                        <!-- Botón Ver más -->
                                       <a href="#" class="btn-ver-mas" 
                                                onclick="toggleTexto(${post.publicacion_id}); return false;">
                                                ${translations[currentLang].verMas}
                                        </a>
                                         <!-- Botón Afiliado -->
                                        ${post.afiliado_link ? `
                                            <a href="#"
                                            class="btn btn-danger mt-2"
                                            rel="nofollow sponsored"
                                            data-ali-redirect="1"
                                            data-pub-id="${post.publicacion_id}"
                                            data-vid="${vid}"
                                            data-user-id="${user_id}"
                                            data-lang="${lang}">
                                            ${comprarTxt}
                                            </a>` : ''}

                                    </div>
                                </div>
                            `;


                        postDisplayContainer.append(cardHtml);
                        cardsRenderizadas++;

                        // 👉 Intercalar popup como “falsa publicación”
                        if (cardsRenderizadas % popupCada === 0) {
                            
                        // insertamos el anchor inmediatamente después de la card recién pintada
                        $(`#card-${post.publicacion_id}`).after(anchorHTML);
                        }
                         // === PRUEBA: agrega 3 popups al final (como la que te funcionó) ===


                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                        // carga mucho la base de datos aplicable cuando hay recursos en cantidad de base de datos

                      //  observeCardImpression(post.publicacion_id);


                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                        // Inicializar la observación de impresiones
                    } else {
                        console.log('Publicación sin contenido:', post.publicacion_id);
                    }
                });

                  localStorage.setItem('categoria', categoria_id); // Guardar la categoría en localStorage
                    document.querySelectorAll('.dpia-spot').forEach(a => {
                    delete a.dataset.renderizado;
                    a.innerHTML = ''; // opcional: limpiar UI anterior
                    });

                    const cp        = localStorage.getItem('codigoPostal');
                    const dominio   = localStorage.getItem('dominio_id');
                    const categoria = localStorage.getItem('categoriaSeleccionadaId');
                    const lang      = localStorage.getItem('language');

                    window.initEmbedPopups({ cp, dominio, categoria, lang });


                
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



function generarEstrellas(rating) {
    const fullStar = '★';
    const emptyStar = '☆';
    const max = 5;
    let estrellasHtml = '';

    for (let i = 1; i <= max; i++) {
        estrellasHtml += i <= Math.floor(rating) ? fullStar : emptyStar;
    }

    // Si hay medio punto (opcional)
    if (rating % 1 >= 0.5 && Math.floor(rating) < max) {
        estrellasHtml = estrellasHtml.substring(0, rating) + '½' + estrellasHtml.substring(rating + 1);
    }

    return estrellasHtml;
}



// Función para extraer precio y descripción del texto
function extraerPrecioYDescripcion(texto) {
    const regex = /^\$ ?(\d+)(.*)/;
    const match = texto.match(regex);

    if (match) {
        const precio = `$${Number(match[1]).toLocaleString()}`;
        const descripcion = match[2].trim();
        return { precio, descripcion };
    } else {
        return { precio: null, descripcion: texto };
    }
}

//const { precio, descripcion } = extraerPrecioYDescripcion(texto);











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
        button.textContent = postText.classList.contains('text-truncated') 
            ? translations[currentLang].verMas 
            : translations[currentLang].verMenos;
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
        window.location.href = `/${publicacionId}/${layout}`;
    }, 500); // 500 ms de retraso para mostrar el splash
}








