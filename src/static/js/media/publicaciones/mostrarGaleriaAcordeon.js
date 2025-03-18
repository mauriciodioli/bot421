
// Función para manejar la lógica del acordeón y cargar publicaciones
function cargarPublicaciones(ambitoId) {
   debugger;
   compara = localStorage.getItem('dominio');
   if(ambitoId!=compara) {
    localStorage.setItem('categoria', '1');
   }

    // Mostrar el splash de carga
    const splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block';
    }

    // Recuperar información del localStorage
    const correo_electronico = localStorage.getItem('correo_electronico');
    const roll = localStorage.getItem('roll');
    const access_token = localStorage.getItem('access_token');
    const codigoPostal = localStorage.getItem('codigoPostal');
 

    if (!access_token) {
        alert("No se ha encontrado el token de acceso.");
        if (splash) splash.style.display = 'none';
        return;
    }
   
    // Verificar si el acordeón con el ID ya existe
    let accordionItem = document.querySelector(`#accordion-content-${ambitoId} .card-grid-publicaciones`);
    
    let lenguaje = localStorage.getItem('language') || 'es'; // Por defecto 'es' si no está definido3
    let categoria = localStorage.getItem('categoria') || '0';

    //if (!accordionItem || accordionItem?.childElementCount === 0 || accordionItem?.textContent.trim() === "") {

            console.log("El acordeón está vacío.");
        
            // Preparar los datos para la solicitud AJAX
            const formData = new FormData();
            formData.append('roll', roll);
            formData.append('correo_electronico', correo_electronico);
            formData.append('layout', 'layout');
            formData.append('ambito', ambitoId); // Pasar el ID del ámbito
            formData.append('lenguaje', lenguaje);
            formData.append('codigoPostal', codigoPostal);
            formData.append('categoria',categoria);

            // Realizar la solicitud AJAX
            $.ajax({
                url: '/media-publicaciones-mostrar/',
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

                 //   if (!accordionContent && publicaciones.length > 0) {
                        // Si el acordeón no existe, crearlo dinámicamente
                        //const accordionContainer = document.querySelector('#postAccordion'); // Contenedor con el ID correcto
                        const accordionContainer = document.querySelector(`#acordeon-${ambitoId}`);
                        console.log(accordionContainer);

                    
                       // var navBarHtml = document.getElementById('navBarCaracteristicasAcordeon').innerHTML;
                       const navBarHtml = `
                                <ul class="nav nav-tabs mt-3" id="listadoCategorias-${ambitoId}" role="tablist">
                                        <li class="nav-item" role="presentation">
                                            <button class="nav-link active" id="home-tab-${ambitoId}" data-bs-toggle="tab" data-bs-target="#home-tab-pane-${ambitoId}" type="button" role="tab" aria-controls="home-tab-pane-${ambitoId}" aria-selected="true">Home</button>
                                        </li>
                                        <li class="nav-item dropdown" role="presentation">
                                            <button class="nav-link dropdown-toggle" style="color: azure;" id="caracteristicas-tab-${ambitoId}" data-bs-toggle="dropdown" type="button" role="tab" aria-expanded="false">Categorías</button>
                                            <ul class="dropdown-menu categoria-dropdown-menu">
                                                <li><a class="dropdown-item categoria-dropdown-item" href="#" data-color="red">Action</a></li>
                                                <li><a class="dropdown-item categoria-dropdown-item" href="#" data-color="green">Another action</a></li>
                                                <li><a class="dropdown-item categoria-dropdown-item" href="#" data-color="orange">Something else here</a></li>
                                                <li><hr class="dropdown-divider"></li>
                                                <li><a class="dropdown-item categoria-dropdown-item" href="#">Separated link</a></li>
                                            </ul>
                                        </li>
                                    </ul>
                                    <div class="tab-content mt-3" id="myTabContent-${ambitoId}">
                                        <div class="tab-pane fade show active" id="home-tab-pane-${ambitoId}" role="tabpanel" aria-labelledby="home-tab-${ambitoId}" tabindex="0">Contenido de Home</div>
                                        <div class="tab-pane fade" id="profile-tab-pane-${ambitoId}" role="tabpanel" aria-labelledby="profile-tab-${ambitoId}" tabindex="0">Contenido de Profile</div>
                                        <div class="tab-pane fade" id="contact-tab-pane-${ambitoId}" role="tabpanel" aria-labelledby="contact-tab-${ambitoId}" tabindex="0">Contenido de Contact</div>
                                        <div class="tab-pane fade" id="disabled-tab-pane-${ambitoId}" role="tabpanel" aria-labelledby="disabled-tab-${ambitoId}" tabindex="0">Contenido Deshabilitado</div>
                                    </div>
                        `;
                   


if (!accordionContainer) {  // Si NO existe, lo creamos
    const newAccordion = `
        <div class="accordion-item" id="acordeon-${ambitoId}"> <!-- Se añade el ID aquí -->
            <h2 class="accordion-header" id="heading-${ambitoId}">
                <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${ambitoId}" aria-expanded="true" aria-controls="collapse-${ambitoId}">
                    ${ambitoId}
                </button>
            </h2>
            <div id="collapse-${ambitoId}" class="accordion-collapse collapse show" aria-labelledby="heading-${ambitoId}" data-bs-parent="#postAccordion">
                <div class="accordion-body" style="background-color: #343a40; color: white;">
                    <div id="accordion-content-${ambitoId}" class="accordion-content">
                        <div id="navBar-${ambitoId}">
                            ${navBarHtml}
                        </div>
                        <div class="card-grid-publicaciones"></div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Insertar el nuevo acordeón en el contenedor principal
    document.querySelector('#postAccordion').insertAdjacentHTML('beforeend', newAccordion);

    agregarEventListenerCategorias(ambitoId);

    // Verificar y agregar CSS solo si no está ya presente
    if (!document.querySelector(`link[href="${cssUrl}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = cssUrl;
        document.head.appendChild(link);
    }

    // Verificar y agregar JS solo si no está ya presente
    if (!document.querySelector(`script[src="${jsUrl}"]`)) {
        const script = document.createElement('script');
        script.src = jsUrl;
        script.defer = true;
        document.head.appendChild(script);
    }
} 

                   
                  //  }
                    
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
                            
                            debugger;
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
       //  } else {
      //      gestionarAcordeones(ambitoId) ;
     //       if (splash) splash.style.display = 'none';
     //   }
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





// Esperar a que el DOM se haya cargado
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todos los elementos de la categoría
    const categoriaItems = document.querySelectorAll('.categoria-dropdown-item');

    // Añadir un evento 'click' a cada elemento
    categoriaItems.forEach(function(item) {
        item.addEventListener('click', function(event) {
            // Prevenir la acción por defecto
            event.preventDefault();

            // Obtener el ID de la categoría y otros atributos
            const categoriaId = item.id;  // id del item (18, 19, 20, etc.)
            const categoriaValor = item.getAttribute('data-value');  // Valor de la categoría (Informática, Electrónica, etc.)
            const categoriaColor = item.getAttribute('data-color');  // Color de la categoría (rojo, verde, azul, etc.)

            // Hacer lo que necesites con la categoría seleccionada, por ejemplo, cargar publicaciones
            console.log(`Categoría seleccionada: ${categoriaValor}, ID: ${categoriaId}, Color: ${categoriaColor}`);
            debugger;
            // Aquí puedes agregar la lógica para filtrar o cargar las publicaciones
            // Puedes llamar a tu función cargarPublicaciones() pasando el ambitoId adecuado
            cargarPublicaciones(categoriaId);  // Ejemplo de uso, si quieres cargar publicaciones basadas en la categoría

        });
    });
});
