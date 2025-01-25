
// Función para manejar la lógica del acordeón y cargar publicaciones
function cargarPublicaciones(ambitoId) {
    // Mostrar el splash de carga
    const splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block';
    }

    // Recuperar información del localStorage
    const correo_electronico = localStorage.getItem('correo_electronico');
    const roll = localStorage.getItem('roll');
    const access_token = localStorage.getItem('access_token');

    if (!access_token) {
        alert("No se ha encontrado el token de acceso.");
        if (splash) splash.style.display = 'none';
        return;
    }
   
    // Verificar si el acordeón con el ID ya existe
    let accordionItem = document.querySelector(`#accordion-content-${ambitoId} .card-grid-publicaciones`);


    if (!accordionItem) {
            // Preparar los datos para la solicitud AJAX
            const formData = new FormData();
            formData.append('roll', roll);
            formData.append('correo_electronico', correo_electronico);
            formData.append('layout', 'layout');
            formData.append('ambito', ambitoId); // Pasar el ID del ámbito

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
                    const publicaciones = response || []; // Acceder directamente al objeto recibido
                    limpiarAcordeon(ambitoId); 
                    // Verificar si el acordeón existe
                    let accordionContent = document.querySelector(`#accordion-content-${ambitoId} .card-grid-publicaciones`);

                    if (!accordionContent && publicaciones.length > 0) {
                        // Si el acordeón no existe, crearlo dinámicamente
                        const accordionContainer = document.querySelector('#postAccordion'); // Contenedor con el ID correcto
                        
                        if (accordionContainer) {
                            const newAccordion = `
                                        <div class="accordion-item">
                                                    <h2 class="accordion-header" id="heading-${ambitoId}">
                                                        <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${ambitoId}" aria-expanded="true" aria-controls="collapse-${ambitoId}">
                                                            ${ambitoId}
                                                        </button>
                                                    </h2>
                                                <div id="collapse-${ambitoId}" class="accordion-collapse collapse show" aria-labelledby="heading-${ambitoId}" data-bs-parent="#postAccordion">

                                                        <div class="accordion-body">
                                                            <div id="accordion-content-${ambitoId}" class="accordion-content">
                                                                <div class="card-grid-publicaciones"> <!-- Aquí se aplica la clase de grilla -->
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            `;
                            accordionContainer.insertAdjacentHTML('beforeend', newAccordion);
                            // Usar un pequeño retraso para asegurarse de que el DOM se actualice
                            
                        
                        
                            // Actualizar la referencia para el contenido del acordeón recién creado
                        
                            accordionContent = document.querySelector(`#accordion-content-${ambitoId} .card-grid-publicaciones`);
                            
                        }
                    }
                    
                    // Ahora que el acordeón existe, limpiar y actualizar su contenido
                    if (accordionContent&& publicaciones.length > 0) {
                        
                        accordionContent.innerHTML = ''; // Limpiar contenido existente
                    
                        publicaciones.forEach(function (post) {
                            let mediaHtml = '';        
                                        
                            if (Array.isArray(post.imagenes) && post.imagenes.length > 0  || post.videos.length > 0) {
                        
                                if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                                    // Si hay imágenes, usar la primera
                                    var firstImageUrl = post.imagenes[0].filepath;
                                    mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
                                } else if (Array.isArray(post.videos) && post.videos.length > 0) {
                                   
                                    // Si no hay imágenes pero hay videos, usar el primero
                                    var firstVideoUrl = post.videos[0].filepath;
                                    console.log(post.videos[0].filepath);
                                    mediaHtml += `
                                            <video controls onclick="abrirModal(${post.publicacion_id})">
                                                <source src="${firstVideoUrl}" type="video/mp4">                                           
                                                Tu navegador no soporta la reproducción de videos.
                                            </video>
                                        `;
                                } else {
                                    // Si no hay ni imágenes ni videos, mostrar un mensaje o imagen por defecto
                                    mediaHtml += `<p>No hay contenido multimedia disponible.</p>`;
                                }
                           
                            }
                            

                            const cardHtml = `
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
                    }

                    // Ocultar el splash después de cargar
                    if (splash) splash.style.display = 'none';


                },
                error: function (error) {
                    console.error("Error al cargar las publicaciones:", error);
                    if (splash) splash.style.display = 'none';
                }
            });
        } else {
            gestionarAcordeones(ambitoId) ;
            if (splash) splash.style.display = 'none';
        }
}






/**
 * Limpia el contenido del encabezado y la grilla de un acordeón dado su ID.
 * @param {string} ambitoId - El ID del ámbito del acordeón a limpiar.
 */
function limpiarAcordeon(ambitoId) {
   // Limpiar el contenido del encabezado del acordeón
    const headerToClear = document.querySelector('#heading-ambito-0');

    // Limpiar el contenido de la grilla (contenido dinámico del acordeón)
    const gridToClear = document.querySelector('#accordion-content-ambito-0');

    // Verificar si el encabezado existe y limpiar su contenido
    if (headerToClear) {
        headerToClear.innerHTML = ''; // Limpia todo el contenido del encabezado
        console.log('Contenido del <h2> limpiado con éxito.');
    } else {
        console.warn('El elemento <h2> no se encontró.');
    }

    // Verificar si la grilla existe y limpiar su contenido
    if (gridToClear) {
        gridToClear.innerHTML = ''; // Limpia todo el contenido de la grilla
        console.log('Contenido de la grilla limpiado con éxito.');
    } else {
        console.warn('El elemento de la grilla no se encontró.');
    }

}


/**
 * Cierra todos los acordeones desplegados y abre el acordeón correspondiente al ID proporcionado.
 * @param {string} ambitoId - El ID del acordeón a desplegar.
 */
function gestionarAcordeones(ambitoId) {
    // Cerrar todos los acordeones desplegados
    const allAccordionButtons = document.querySelectorAll('button.accordion-button');
    allAccordionButtons.forEach((button) => {
        const targetId = button.getAttribute('data-bs-target'); // Obtener el ID del contenido del acordeón
        const targetElement = document.querySelector(targetId);

        if (targetElement && targetElement.classList.contains('show')) {
            targetElement.classList.remove('show'); // Cierra el contenido del acordeón
        }

        button.classList.add('collapsed'); // Cambiar el botón a estado "colapsado"
        button.setAttribute('aria-expanded', 'false'); // Actualizar el atributo de accesibilidad
    });

    // Abrir el acordeón seleccionado
    const accordionContent = document.querySelector(`#collapse-${ambitoId}`);
    const accordionButton = document.querySelector(`#heading-${ambitoId} .accordion-button`);

    if (accordionContent && accordionButton) {
        accordionContent.classList.add('show'); // Mostrar el contenido del acordeón seleccionado
        accordionButton.classList.remove('collapsed'); // Cambiar el botón a estado "desplegado"
        accordionButton.setAttribute('aria-expanded', 'true'); // Actualizar el atributo de accesibilidad

        accordionButton.focus(); // Colocar el foco en el botón seleccionado
        console.log(`Foco establecido y acordeón desplegado para ID: ${ambitoId}`);
    } else {
        console.warn(`No se pudo encontrar el contenido o el botón del acordeón para ID: ${ambitoId}`);
    }
}


