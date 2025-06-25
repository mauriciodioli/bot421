document.addEventListener('DOMContentLoaded', function () {
    // Seleccionamos el primer ítem que tiene el atributo 'data-color'
    const firstItem = document.querySelector('.categoria-dropdown-item[data-color]');

    // Si hay un primer ítem, actualizamos el color
    if (firstItem) {
        updateColor(firstItem);
    }

    // Aseguramos que la lógica solo se ejecute una vez para el primer ítem
    // Esto solo se ejecutará una vez en el evento 'DOMContentLoaded'
});


function updateColor(element) {
   
    console.log(element);
    if (!element) return; // Evita errores si no se pasa un elemento
    
    // Obtener el id del elemento
    let id = element.id;
    let colorElementCategoria = element.getAttribute('data-color');
    //console.log('ID obtenido:', id);
   

    let navTabs = document.querySelector('.nav-tabs');
    let homeTab = document.querySelector('#home-tab'); // Selecciona el botón "Home"

    // Elimina cualquier clase de color existente en la barra y en el botón "Home"
    navTabs.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');
    homeTab.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');

    // Agrega la nueva clase de color para los elementos de la barra
    navTabs.classList.add('border-' + colorElementCategoria);
    homeTab.classList.add('border-' + colorElementCategoria);
}






















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
dropdownMenuCategorias.empty();
// Función para cargar los ámbitos desde el servidor
function cargarAmbitosCategorias() {
   
    // Datos del formulario o de algún elemento que necesites enviar
    let ambito = localStorage.getItem('dominio');
    const cp = localStorage.getItem('codigoPostal');
    
    if(ambito == 'inicialDominio'){ ambito = 'Laboral';}
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
        if (!data || !Array.isArray(data.categorias)) {
            throw new Error("La respuesta de la API no contiene 'categorias' o no es un array.");
        }
        // Limpiar el menú y el contenedor de tarjetas antes de agregar nuevos elementos
        dropdownMenuCategorias.empty();
 

        // Agregar las categorías obtenidas al dropdown
        data.categorias.forEach((categoria, index) => {
            // Agregar la categoría al menú desplegable
            // Asigna un valor predeterminado en caso de que no esté definido
            const color = categoria.color || 'orange'; // O cualquier color predeterminado que desees
            const listItem = `
                        <li style="padding: 10px;">
                            <a href="#" class="categoria-dropdown-item" id="${categoria.id}" data-value="${categoria.valor}" data-color="${color}" style="color: ${color}; padding: 10px;">
                                ${categoria.nombre}
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                    `;

        
            dropdownMenuCategorias.append(listItem);

         
        });

      

        // Eliminar el último separador
        dropdownMenuCategorias.children('li').last().remove();
         // Agregar evento para cerrar el dropdown al hacer clic en una categoría
       
           
       
    })
    .catch(error => {
        console.error('Error al cargar las categorías:', error);
    });
}








// Asegurar que al hacer clic en el botón de categoría, se vuelva a mostrar
$('.categoria-dropdown-toggle').on('click', function (e) {
    e.stopPropagation(); // Evita que el evento se propague y lo cierre inmediatamente
    $('.categoria-dropdown-menu').toggleClass('show'); // Alterna visibilidad
});



// Delegación de eventos para manejar clics en los ítems del menú desplegable
$('.categoria-dropdown-menu').on('click', '.categoria-dropdown-item', function (e) {
//$(document).on('click', '#navBar-' + ambitoId + ' .categoria-dropdown-item', function (e) {

    e.preventDefault(); // Previene el comportamiento predeterminado
   
    let categoriaId = $(this).attr('id');
    let categoriaNombre = $(this).data('value');
    
    console.log("Categoría seleccionada:", categoriaNombre);
    console.log("Clic detectado"); // Para verificar si el clic está siendo detectado
    // Cerrar el menú desplegable correctamente
    $('.categoria-dropdown-menu').removeClass('show'); // Alternativa sin Bootstrap
 //   $('.categoria-dropdown-toggle').dropdown('hide');  // Si usas Bootstrap (el botón que activa el menú)
   
    const selectedCategory = this.id; // Obtiene el valor de data-value
  
    // Guardar el dominio en localStorage
    localStorage.setItem('categoria', selectedCategory);
    var domain = localStorage.getItem('dominio');
    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }
    $('#home-tab').text(this.dataset.value);  // Cambiar el texto del botón con el valor de 'selectedCategory'
    // Mostrar en consola
  
    console.log('Dominio enviado desde categorias---------------:', domain);
    console.log('Categorias---------------:', selectedCategory);
    // Llamar a la función para manejar el dominio seleccionado
    
    if (document.querySelector('#navBarCaracteristicas-home')) {
        console.log("Ejecutando en home.html");
       
        cargarPublicaciones(domain, 'layout');
    }
    if (document.querySelector('#navBarCaracteristicas-index')) {
        console.log("Ejecutando en index.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
    } 
    
    
    // Marcar el ítem como activo
    $('.categoria-dropdown-item').removeClass('active');
    $(this).addClass('active');
     
    updateColor($(this)[0]); // Convierte jQuery a elemento DOM puro

});












// Delegación de eventos para manejar clics en las tarjetas
$('.card-container').on('click', '.card', function () {
    const selectedCategory = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();

    // Guardar el dominio en localStorage
    localStorage.setItem('categoria', selectedCategory);
    var domain = localStorage.getItem('dominio');
    // Actualizar el input oculto
    const hiddenInput = $('#domain'); // Usamos jQuery para seleccionar el input
    if (hiddenInput.length) {
        hiddenInput.val(selectedCategory);
    }
    console.log('hiddenInput:', hiddenInput.val());
    // Mostrar en consola
    console.log('Categoria seleccionada---------------:', selectedCategory);
    
     if (document.querySelector('#navBarCaracteristicas-home')) {
        console.log("Ejecutando en home.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
    }else{
        console.log("Ejecutando en index.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
    } 
    if (document.querySelector('#navBarCaracteristicas-mostrarGaleria')) {
        console.log("Ejecutando en mostrarGaleria.html");
        enviarDominioAJAXDesdeCategorias(domain,selectedCategory);
   
    }

    // Marcar la tarjeta como activa
    $('.card').removeClass('active');
    $(this).addClass('active');

    // Enfocar la sección
    $('.dpi-muestra-publicaciones-centrales')[0].focus();
});

// Llamar a la función para cargar los ámbitos al cargar la página
cargarAmbitosCategorias();




  


























function enviarDominioAJAXDesdeCategorias(domain,selectedCategory) {    
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
   
    if ( !localStorage.getItem('categoria')) {        
        localStorage.setItem('categoria', '1');
       
    }

   


   
    // Esperar a que se actualice el idioma en localStorage antes de continuar
    setTimeout(() => {
        
                let lenguaje = localStorage.getItem('language'); // Por defecto 'es' si no está definido


                $.ajax({
                type: 'POST',
                url: galeriaURL,
                dataType: 'json', // Asegúrate de que el backend devuelva un JSON
                headers: { 'Authorization': 'Bearer ' + access_token }, // Enviar el token en el encabezado
                data: { ambitos: domain,
                        categoria: selectedCategory, 
                        lenguaje: lenguaje}, // Enviar el dominio como parte de los datos
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


