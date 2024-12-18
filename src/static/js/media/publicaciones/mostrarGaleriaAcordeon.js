// Escuchar el evento de apertura del acordeón
////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////
///////////////////no funciona nada de esto//////////////// le puse 1 para que no tome esto
document.addEventListener('show.bs.collapse1', function (event) {
    // Obtener el elemento del acordeón que se está abriendo
    var accordionItem = event.target;
    var ambitoId = accordionItem.getAttribute('id').replace('collapse-', ''); // Extraer el ID del ámbito

    // Mostrar el splash de carga
    var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block';
    }

    // Recuperar información del localStorage
    var correo_electronico = localStorage.getItem('correo_electronico');
    var roll = localStorage.getItem('roll');
    var access_token = localStorage.getItem('access_token');

    if (!access_token) {
        alert("No se ha encontrado el token de acceso.");
        if (splash) splash.style.display = 'none';
        return;
    }

    // Preparar los datos para la solicitud AJAX
    var formData = new FormData();
    formData.append('roll', roll);
    formData.append('correo_electronico', correo_electronico);
    formData.append('layout', 'layout');
    formData.append('ambito_id', ambitoId); // Pasar el ID del ámbito

    // Realizar la solicitud AJAX
    $.ajax({
        url: '/media-publicaciones-mostrar',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        headers: {
            'Authorization': 'Bearer ' + access_token
        },
        success: function (response) {
            var publicaciones = response.publicaciones || [];
            var accordionContent = document.querySelector(`#accordion-content-${ambitoId} .card-grid-publicaciones`);
            accordionContent.innerHTML = ''; // Limpiar contenido existente

            publicaciones.forEach(function (post) {
                var mediaHtml = '';
                if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                    var firstImageUrl = post.imagenes[0].filepath;
                    mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
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
                accordionContent.insertAdjacentHTML('beforeend', cardHtml);
            });
           // user_id = response.user_id
            //obtenerAmbitos(id)
            if (splash) splash.style.display = 'none'; // Ocultar el splash después de cargar
        },
        error: function (error) {
            console.error("Error al cargar las publicaciones:", error);
            if (splash) splash.style.display = 'none';
        }
    });
});





function obtenerAmbitos(id) {
    // Mostrar el splash (asumo que existe una variable splash definida)
    var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block';
    }

    // Realizar la solicitud fetch
    fetch('/social-media-publicaciones-obtener-ambitos')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            // Ocultar el splash después de recibir la respuesta
            if (splash) {
                splash.style.display = 'none';
            }

            if (Array.isArray(data)) {
                var postAccordion = $('#postAccordion');
                postAccordion.empty();

                // Organizar publicaciones por ámbito
                var postsByAmbito = {};
                data.forEach(function(post) {
                    if (!postsByAmbito[post.ambito]) {
                        postsByAmbito[post.ambito] = [];
                    }
                    postsByAmbito[post.ambito].push(post);
                });

                // Crear secciones del acordeón
                Object.keys(postsByAmbito).forEach(function(ambito, index) {
                    var ambitoId = 'ambito-' + index; // ID único para cada ámbito
                    var publicaciones = postsByAmbito[ambito];

                    // HTML del acordeón
                    var accordionItemHtml = `
                        <div class="accordion-item">
                            <h2 class="accordion-header" id="heading-${ambitoId}">
                                <button class="accordion-button" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#collapse-${ambitoId}" 
                                    aria-expanded="true" aria-controls="collapse-${ambitoId}">
                                    ${ambito}
                                </button>
                            </h2>
                            <div id="collapse-${ambitoId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" 
                                aria-labelledby="heading-${ambitoId}" data-bs-parent="#postAccordion">
                                <div class="accordion-body">
                                    <div id="accordion-content-${ambitoId}" class="accordion-content">
                                        <div class="card-grid-publicaciones">
                                            ${publicaciones.map(post => `
                                                <div class="card">
                                                    <div class="card-body">
                                                        <h5 class="card-title">${post.titulo || 'Sin título'}</h5>
                                                        <p class="card-text">${post.descripcion || 'Sin descripción'}</p>
                                                    </div>
                                                </div>
                                            `).join('')}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;

                    postAccordion.append(accordionItemHtml);
                });
            }
        })
        .catch(error => {
            if (splash) {
                splash.style.display = 'none';
            }
            alert('Error al obtener los ámbitos: ' + error.message);
            console.error(error);
        });
}
