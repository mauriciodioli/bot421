

document.querySelectorAll('.categoria-dropdown-item').forEach(item => {
    item.addEventListener('click', function (event) {
        event.preventDefault(); // Evita que el enlace recargue la página

        let color = this.getAttribute('data-color'); // Obtiene el color del atributo
        if (!color) return; // Si no hay color, no hacer nada

        let navTabs = document.querySelector('.nav-tabs');
        let homeTab = document.querySelector('#home-tab'); // Selecciona el botón "Home"

        // Elimina cualquier clase de color existente en la barra y en el botón "Home"
        navTabs.classList.remove('border-red', 'border-green', 'border-orange');
        homeTab.classList.remove('border-red', 'border-green', 'border-orange');

        // Agrega la nueva clase de color
        navTabs.classList.add('border-' + color);
        homeTab.classList.add('border-' + color);
    });
});





















// Agregar un manejador de eventos de clic al botón
$('#caracteristicas-tab').on('click', function() {
    // Llamar a la función para cargar los ámbitos
    banderaCategorias = localStorage.getItem('banderaCategorias');
    if (banderaCategorias == 'True') {
        cargarAmbitosCategorias();   
        localStorage.setItem('banderaCategorias', 'False');
    }  
});




const dropdownMenuCategorias = $('.categoria-dropdown-menu');

// Función para cargar los ámbitos desde el servidor
function cargarAmbitosCategorias() {
    // Datos del formulario o de algún elemento que necesites enviar
    const ambito = localStorage.getItem('dominio');
    const cp = localStorage.getItem('codigoPostal');
    
    const formData = new FormData();
    formData.append('ambito', ambito);  // Cambia 'nombre_del_ambito' con el valor que necesites
    formData.append('cp', cp);  // Cambia 'codigo_postal' con el valor correspondiente

    fetch('/social-media-ambitosCategorias-categoria-mostrar/', {
        method: 'POST',
        body: formData,  // Enviar los datos del formulario
        headers: {
            'Accept': 'application/json',  // Esperar JSON de respuesta
            // Si el backend requiere algún tipo de encabezado adicional (como tokens de autenticación), agrégalo aquí
        }
    })
    .then(response => response.json())
    .then(data => {
        // Aquí manejas la respuesta de la API, por ejemplo, agregando los elementos a la interfaz

        // Limpiar el menú y el contenedor de tarjetas antes de agregar nuevos elementos
        dropdownMenuCategorias.empty();
        $('.card-container').empty();

        // Agregar las categorías obtenidas al dropdown
        data.categorias.forEach((categoria, index) => {
            // Agregar la categoría al menú desplegable
            const listItem = `
                <li>
                    <a href="#" class=" categoria-dropdown-item" id="${categoria.valor}">
                        ${categoria.nombre}
                    </a>
                </li>
                <li><hr class="dropdown-divider"></li>
            `;
            dropdownMenuCategorias.append(listItem);

            // Crear una nueva tarjeta para cada categoría
            const categoryCard = `
                <div class="category-card${index + 1} card" id="card-${categoria.valor}">
                    <div class="card-content">                              
                        <p class="card-number">${categoria.nombre}</p>
                    </div>
                </div>
            `;
            $('.card-container').append(categoryCard);
        });

      

        // Eliminar el último separador
        dropdownMenuCategorias.children('li').last().remove();
    })
    .catch(error => {
        console.error('Error al cargar las categorías:', error);
    });
}

// Delegación de eventos para manejar clics en los ítems del menú desplegable
$('.categoria-dropdown-menu').on('click', '.categoria-dropdown-item', function (e) {
    e.preventDefault(); // Previene el comportamiento predeterminado

    const selectedCategory = this.id; // ID del ítem clickeado

    // Guardar el dominio en localStorage
    localStorage.setItem('categoria', selectedCategory);

    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }
    $('#home-tab').text(selectedCategory);  // Cambiar el texto del botón con el valor de 'selectedCategory'
    // Mostrar en consola
    console.log('Dominio seleccionado:', selectedCategory);
    
    // Llamar a la función para manejar el dominio seleccionado
    enviarDominioAJAXDesdeCategorias(selectedCategory);

    // Marcar el ítem como activo
    $('.categoria-dropdown-item').removeClass('active');
    $(this).addClass('active');
});

// Delegación de eventos para manejar clics en las tarjetas
$('.card-container').on('click', '.card', function () {
    const selectedCategory = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();

    // Guardar el dominio en localStorage
    localStorage.setItem('categoria', selectedCategory);

    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }

    // Mostrar en consola
    console.log('Dominio seleccionado:', selectedCategory);
    
    // Llamar a la función para manejar el dominio seleccionado
    enviarDominioAJAXDesdeCategorias(selectedCategory);

    // Marcar la tarjeta como activa
    $('.card').removeClass('active');
    $(this).addClass('active');

    // Enfocar la sección
    $('.dpi-muestra-publicaciones-centrales')[0].focus();
});

// Llamar a la función para cargar los ámbitos al cargar la página
cargarAmbitosCategorias();




  


























function enviarDominioAJAXDesdeCategorias(domain) {    
    // Elementos relevantes
    const splash = document.querySelector('.splashCarga');
    const targetSection = document.querySelector('.dpi-muestra-publicaciones-centrales'); // Asegúrate de que esta clase esté bien definida

    if (!splash || !targetSection) {
        console.error("No se encontró el elemento 'splashCarga' o la sección 'domains'.");
        return;
    }

    // Mostrar/ocultar splash según la visibilidad de la sección
    toggleSplash(targetSection, splash);

    // Ruta al archivo con la galería de imágenes   
    var galeriaURL = '/media-publicaciones-mostrar-dpi/';
    var access_token = 'access_dpi_token_usuario_anonimo';

    if ( !localStorage.getItem('categorias')) {
        
        localStorage.setItem('categoria', domain);
       
    }

   


   
    // Esperar a que se actualice el idioma en localStorage antes de continuar
    setTimeout(() => {
        
                let lenguaje = localStorage.getItem('language'); // Por defecto 'es' si no está definido


                $.ajax({
                type: 'POST',
                url: galeriaURL,
                dataType: 'json', // Asegúrate de que el backend devuelva un JSON
                headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
                data: { ambitos: domain, lenguaje: lenguaje}, // Enviar el dominio como parte de los datos
                success: function (response) {
                // console.log('Respuesta del servidor:', response[0].ambito);
                  

                    splash.style.display = 'none'; // Ocultar el splash al terminar
                    if (Array.isArray(response)) {
                        var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                        postDisplayContainer.empty();

                        response.forEach(function(post) {
                            if (post.imagenes.length > 0 || post.videos.length > 0) {
                                    var mediaHtml = '';

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
                                                    <video controls  style="cursor: pointer;" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                                        <source src="${firstVideoUrl}" type="video/mp4">                                           
                                                        Tu navegador no soporta la reproducción de videos.
                                                    </video>
                                                `;

                                        } else {
                                            // Si no hay ni imágenes ni videos, mostrar un mensaje o imagen por defecto
                                            mediaHtml += `<p>No hay contenido multimedia disponible.</p>`;
                                        }

                                    
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


    }, 2000); // Esperamos 2 segundos para asegurar que `getLocation()` actualice `language`


}


