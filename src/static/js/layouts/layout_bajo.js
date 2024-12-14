$(document).ready(function () {
    // Manejador de eventos para cada ítem del menú
    $('.custom-dropdown-menu .dropdown-item').on('click', function (e) {
        e.preventDefault();
        const selectedItem = $(this).attr('id');
        localStorage.setItem('dominio', selectedItem);
        cargarPublicaciones(selectedItem, 'layout');
    });

    // Mostrar u ocultar el menú desplegable al hacer clic en el botón
    $('.close-layout-btn').on('click', function () {
        $('.custom-dropdown-menu').toggle();
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
            dropdownMenu.style.display = "none";
        });
    });
});
