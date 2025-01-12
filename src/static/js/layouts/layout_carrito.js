$(document).ready(function () {
    // Manejador de eventos para cada ítem del menú
    $('.custom-dropdown-menu .dropdown-item').on('click', function (e) {
        e.preventDefault();
        const selectedItem = $(this).attr('id');
        localStorage.setItem('dominio', selectedItem);
        cargarPublicaciones(selectedItem, 'layout');

        // Ocultar el menú después de hacer clic en un ítem
        $('.custom-dropdown-menu').hide();
    });

    // Mostrar u ocultar el menú desplegable al hacer clic en el botón
    $('.close-layout-btn').on('click', function () {
        $('.custom-dropdown-menu').toggle();
    });

    // Evitar que el menú se cierre cuando se haga clic dentro del contenedor
    $('.custom-dropdown-menu').on('click', function(e) {
        e.stopPropagation(); // Evitar que se propague el clic y cierre el menú
    });

    // Cerrar el layout al hacer clic en el botón de cerrar
    $('#closeLayout').on('click', function () {
        $('#bottomLayout').addClass('hidden');
    });

    // Mantener la funcionalidad de mostrar/ocultar el layout con scroll
    let lastScrollTop = 0; // Última posición del scroll
    let scrolling = false; // Estado de scroll en curso

    $(window).on('scroll', function () {
        scrolling = true;

        // Obtener la posición actual del scroll
        const currentScrollTop = $(this).scrollTop();

        if (currentScrollTop > lastScrollTop) {
            // Scroll hacia abajo -> ocultar el layout
            $('#bottomLayout').addClass('hidden');
        } else {
            // Scroll hacia arriba -> mostrar el layout
            $('#bottomLayout').removeClass('hidden');
        }

        lastScrollTop = currentScrollTop; // Actualizar la última posición del scroll
    });

    // Comprobar si el usuario está en reposo (sin scroll) después de 2 segundos
    setInterval(function () {
        if (!scrolling) {
            $('#bottomLayout').removeClass('hidden'); // Mostrar el layout si no hay scroll
        }
        scrolling = false; // Reiniciar el estado de scroll
    }, 2000);
});

document.addEventListener("DOMContentLoaded", () => {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const dropdownContainer = document.getElementById("dropdownContainer");
    
    if (!dropdownButton || !dropdownMenu || !dropdownContainer) {
        console.error("Uno o más elementos no existen en el DOM.");
        return;
    }

    // Mostrar el menú al hacer clic en el botón
    dropdownButton.addEventListener("click", (event) => {
        event.stopPropagation(); // Evita que el clic cierre el menú
        dropdownMenu.style.display =
            dropdownMenu.style.display === "flex" ? "none" : "flex";
    });

    // Cerrar el menú cuando se haga clic fuera del contenedor
    document.addEventListener("click", () => {
        dropdownMenu.style.display = "none";
    });

    // Evitar que el menú se cierre al hacer clic dentro del contenedor
    dropdownContainer.addEventListener("click", (event) => {
        event.stopPropagation();
    });

    // Cerrar el menú al seleccionar un elemento
    dropdownMenu.querySelectorAll("a").forEach((item) => {
        item.addEventListener("click", () => {
            dropdownMenu.style.display = "none"; // Cerrar menú después de seleccionar un ítem
        });
    });
});
















document.addEventListener('DOMContentLoaded', function () {

    
    const dropdownMenu = document.querySelector('.custom-dropdown-menu');

    // Función para cargar los ámbitos desde el servidor
    function cargarAmbitos() {
        fetch('/social-media-publicaciones-obtener-ambitos', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Error al obtener los ámbitos.');
            }
            return response.json();
        })
        .then(data => {
            // Limpiar el menú existente
            dropdownMenu.innerHTML = '';

            // Agregar los ámbitos dinámicamente al menú
            data.forEach(ambito => {
                const listItem = document.createElement('li');
                const anchor = document.createElement('a');
                anchor.className = 'dropdown-item';
                anchor.id = ambito.nombre.toLowerCase();
                anchor.href = '#';
                anchor.textContent = ambito.nombre;

                listItem.appendChild(anchor);
                dropdownMenu.appendChild(listItem);

                // Agregar separadores si es necesario
                const divider = document.createElement('li');
                divider.innerHTML = '<hr class="dropdown-divider">';
                dropdownMenu.appendChild(divider);
            });

            // Eliminar el último separador
            if (dropdownMenu.lastChild) {
                dropdownMenu.removeChild(dropdownMenu.lastChild);
            }

            // Agregar evento click a los elementos recién creados
            agregarEventosClick();
        })
        .catch(error => {
            console.error('Error al cargar los ámbitos:', error);
        });
    }

    // Función para manejar clics en los elementos del menú
    function agregarEventosClick() {
        const menuItems = document.querySelectorAll('.custom-dropdown-menu .dropdown-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function (event) {
                event.preventDefault();
                const ambito = this.textContent; // Obtener el texto del elemento clicado
              
            });
        });
    }

  

    // Llamar a la función para cargar los ámbitos al cargar la página
    cargarAmbitos();
});

















