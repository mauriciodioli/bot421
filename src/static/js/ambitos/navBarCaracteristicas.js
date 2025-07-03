// Esperar a que jQuery esté disponible
(function() {
    function initNavBarCaracteristicas() {
        // Verificar si jQuery está disponible
        if (typeof $ === 'undefined') {
            console.error('jQuery no está disponible. Reintentando en 100ms...');
            setTimeout(initNavBarCaracteristicas, 100);
            return;
        }

        console.log('jQuery disponible, inicializando navBarCaracteristicas.js');

        // TODO EL CÓDIGO ORIGINAL VA AQUÍ, PERO ENVUELTO EN $(document).ready()
        $(document).ready(function() {
            
            // Seleccionamos el primer ítem que tiene el atributo 'data-color'
            const firstItem = document.querySelector('.categoria-dropdown-item[data-color]');

            // Si hay un primer ítem, actualizamos el color
            if (firstItem) {
                updateColor(firstItem);
            }

            // MANEJADOR ÚNICO PARA EL BOTÓN DE CATEGORÍAS
            $('#caracteristicas-tab').off('click').on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Clic en categorías detectado'); // Debug
                
                // Llamar a la función para cargar los ámbitos
                let banderaCategorias = localStorage.getItem('banderaCategorias');
                if (banderaCategorias == 'True') {
                    console.log('Cargando categorías...'); // Debug
                    cargarAmbitosCategorias();   
                    localStorage.setItem('banderaCategorias', 'False');
                }
                
                // Alternar la visibilidad del dropdown
                const dropdownMenu = $('.categoria-dropdown-menu');
                const isVisible = dropdownMenu.hasClass('show');
                
                if (isVisible) {
                    dropdownMenu.removeClass('show');
                    $(this).removeClass('active');
                    console.log('Cerrando dropdown'); // Debug
                } else {
                    dropdownMenu.addClass('show');
                    $(this).addClass('active');
                    console.log('Abriendo dropdown'); // Debug
                }
            });

            // DELEGACIÓN DE EVENTOS PARA SUBCATEGORÍAS
            $('.categoria-dropdown-menu').off('click').on('click', '.categoria-dropdown-item', function (e) {
                e.preventDefault();
                e.stopPropagation();
               
                let categoriaId = $(this).attr('id');
                let categoriaNombre = $(this).data('value');
                
                console.log("Subcategoría seleccionada:", categoriaNombre);
                console.log("ID:", categoriaId);
                
                // Cerrar el menú desplegable correctamente
                $('.categoria-dropdown-menu').removeClass('show');
                $('#caracteristicas-tab').removeClass('active');
               
                const selectedCategory = this.id;
              
                // Guardar el dominio en localStorage
                localStorage.setItem('categoria', selectedCategory);
                var domain = localStorage.getItem('dominio');
                
                // Actualizar el input oculto
                const hiddenInput = $('#domain');
                if (hiddenInput.length) {
                    hiddenInput.val(selectedCategory);
                }
                
                $('#home-tab').text(this.dataset.value);
                
                // Mostrar en consola
                console.log('Dominio enviado desde categorias:', domain);
                console.log('Categorias:', selectedCategory);
                
                // Llamar a la función para manejar el dominio seleccionado
                if (document.querySelector('#navBarCaracteristicas-home')) {
                    console.log("Ejecutando en home.html");
                    cargarPublicaciones(domain, 'layout');
                }
                if (document.querySelector('#navBarCaracteristicas-index')) {
                    console.log("Ejecutando en index.html");
                    enviarDominioAJAXDesdeCategorias(domain, selectedCategory);
                } 
                
                // Marcar el ítem como activo
                $('.categoria-dropdown-item').removeClass('active');
                $(this).addClass('active');
                 
                updateColor($(this)[0]);
            });

            // Cerrar el dropdown cuando se hace clic fuera de él
            $(document).off('click.dropdown').on('click.dropdown', function(e) {
                if (!$(e.target).closest('.nav-item.dropdown').length) {
                    $('.categoria-dropdown-menu').removeClass('show');
                    $('#caracteristicas-tab').removeClass('active');
                }
            });

            // Delegación de eventos para manejar clics en las tarjetas
            $('.card-container').on('click', '.card', function () {
                const selectedCategory = $(this).find('.card-number').text().replace(/[^\w\sáéíóúÁÉÍÓÚüÜ]/g, '').trim();

                localStorage.setItem('categoria', selectedCategory);
                var domain = localStorage.getItem('dominio');
                
                const hiddenInput = $('#domain');
                if (hiddenInput.length) {
                    hiddenInput.val(selectedCategory);
                }
                
                console.log('Categoria seleccionada desde tarjeta:', selectedCategory);
                
                if (document.querySelector('#navBarCaracteristicas-home')) {
                    console.log("Ejecutando en home.html");
                    enviarDominioAJAXDesdeCategorias(domain, selectedCategory);
                } else {
                    console.log("Ejecutando en index.html");
                    enviarDominioAJAXDesdeCategorias(domain, selectedCategory);
                } 
                
                if (document.querySelector('#navBarCaracteristicas-mostrarGaleria')) {
                    console.log("Ejecutando en mostrarGaleria.html");
                    enviarDominioAJAXDesdeCategorias(domain, selectedCategory);
                }

                $('.card').removeClass('active');
                $(this).addClass('active');

                // ELIMINAR ESTA LÍNEA QUE CAUSA EL SCROLL HACIA ARRIBA
                // $('.dpi-muestra-publicaciones-centrales')[0].focus();
            });

            // Llamar a la función para cargar los ámbitos al cargar la página
            cargarAmbitosCategorias();

        }); // Fin de $(document).ready()

    } // Fin de initNavBarCaracteristicas()

    // FUNCIONES FUERA DEL $(document).ready() pero dentro del wrapper
    function updateColor(element) {
        console.log('Actualizando color:', element);
        if (!element) return;
        
        let id = element.id;
        let colorElementCategoria = element.getAttribute('data-color');

        let navTabs = document.querySelector('.nav-tabs');
        let homeTab = document.querySelector('#home-tab');

        if (navTabs && homeTab) {
            navTabs.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');
            homeTab.classList.remove('border-red', 'border-green', 'border-blue', 'border-orange');

            navTabs.classList.add('border-' + colorElementCategoria);
            homeTab.classList.add('border-' + colorElementCategoria);
        }
    }

    function cargarAmbitosCategorias() {
        let ambito = localStorage.getItem('dominio');
        const cp = localStorage.getItem('codigoPostal');
        
        if(ambito == 'inicialDominio'){ ambito = 'Laboral';}
        
        const dropdownMenuCategorias = $('.categoria-dropdown-menu');
        dropdownMenuCategorias.empty();
        
        const formData = new FormData();
        formData.append('ambito', ambito);
        formData.append('cp', cp || '');

        console.log('Cargando subcategorías para:', ambito, 'CP:', cp);

        fetch('/social-media-ambitosCategorias-categoria-mostrar/', {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Subcategorías recibidas:', data);
            
            if (!data || !Array.isArray(data.categorias)) {
                throw new Error("La respuesta de la API no contiene 'categorias' o no es un array.");
            }
            
            dropdownMenuCategorias.empty();

            data.categorias.forEach((categoria, index) => {
                const color = categoria.color || 'orange';
                const listItem = `
                    <li style="padding: 10px;">
                        <a href="#" class="categoria-dropdown-item" id="${categoria.id}" data-value="${categoria.valor}" data-color="${color}" style="color: ${color}; padding: 10px;">
                            ${categoria.nombre}
                        </a>
                    </li>
                    ${index < data.categorias.length - 1 ? '<li><hr class="dropdown-divider"></li>' : ''}
                `;
                dropdownMenuCategorias.append(listItem);
            });
            
            console.log('Subcategorías cargadas correctamente');
        })
        .catch(error => {
            console.error('Error al cargar las categorías:', error);
        });
    }

    function enviarDominioAJAXDesdeCategorias(domain, selectedCategory) {    
        console.log('=== CARGANDO PUBLICACIONES DESDE SUBCATEGORÍA ===');
        console.log('Domain:', domain, 'Category:', selectedCategory);
        
        const splash = document.querySelector('.splashCarga');
        const targetSection = document.querySelector('.dpi-muestra-publicaciones-centrales');

        if (!splash || !targetSection) {
            console.error("No se encontró el elemento 'splashCarga' o la sección target.");
            return;
        }

        splash.style.display = 'block';
        
        var galeriaURL = '/media-publicaciones-mostrar-dpi/';
        var access_token = 'access_dpi_token_usuario_anonimo';
        const cp = localStorage.getItem('codigoPostal');
       
        if (!localStorage.getItem('categoria')) {        
            localStorage.setItem('categoria', '1');
        }

        setTimeout(() => {
            let lenguaje = localStorage.getItem('language') || 'in';

            $.ajax({
                type: 'POST',
                url: galeriaURL,
                dataType: 'json',
                headers: { 'Authorization': 'Bearer ' + access_token },
                data: { 
                    ambitos: domain,
                    categoria: selectedCategory, 
                    lenguaje: lenguaje,
                    cp: cp || ''
                },
                success: function (response) {
                    console.log('=== RESPUESTA EXITOSA ===');
                    console.log('Response:', response);
                    
                    splash.style.display = 'none';
                    
                    if (Array.isArray(response)) {
                        var postDisplayContainer = $('.dpi-muestra-publicaciones-centrales');
                        postDisplayContainer.empty();

                        response.forEach(function(post) {
                            if (post.imagenes.length > 0 || post.videos.length > 0) {
                                var mediaHtml = '';

                                if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                                    if (post.imagenes[0].imagen != null) {
                                        var firstImageBase64 = post.imagenes[0].imagen;
                                        var firstImageUrl = `data:${post.imagenes[0].mimetype};base64,${firstImageBase64}`;
                                        mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                    } else {
                                        var firstImageUrl = post.imagenes[0].filepath;
                                        mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')" style="cursor: pointer;">`;
                                    }
                                } else if (Array.isArray(post.videos) && post.videos.length > 0) {
                                    var firstVideoUrl = post.videos[0].filepath;
                                    mediaHtml += `
                                        <video controls style="cursor: pointer;" onclick="abrirPublicacionHome(${post.publicacion_id}, '${post.layout}')">
                                            <source src="${firstVideoUrl}" type="video/mp4">
                                            Tu navegador no soporta la reproducción de videos.
                                        </video>
                                    `;
                                }

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
                            }
                        });
                        
                        console.log('Publicaciones cargadas, haciendo scroll...');
                        
                        // SCROLL SUAVE HACIA LAS PUBLICACIONES DESPUÉS DE CARGAR
                        setTimeout(() => {
                            targetSection.scrollIntoView({ 
                                behavior: 'smooth', 
                                block: 'start' 
                            });
                        }, 100);
                        
                    } else {
                        console.error("La respuesta no es un array:", response);
                    }
                },
                error: function (xhr, status, error) {
                    splash.style.display = 'none';
                    console.error('=== ERROR EN AJAX ===');
                    console.error('Status:', status, 'Error:', error);
                    console.error('Response:', xhr.responseText);
                }
            });
        }, 500); // Reducido de 2000 a 500ms
    }

    // Exponer funciones globalmente si es necesario
    window.updateColor = updateColor;
    window.cargarAmbitosCategorias = cargarAmbitosCategorias;
    window.enviarDominioAJAXDesdeCategorias = enviarDominioAJAXDesdeCategorias;

    // Inicializar cuando se cargue la página
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNavBarCaracteristicas);
    } else {
        initNavBarCaracteristicas();
    }

})(); // IIFE - Immediately Invoked Function Expression


