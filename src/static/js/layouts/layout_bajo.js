$(document).ready(function() {
    // No necesitamos mostrarlo después de 1 segundo porque ya está visible

    // Función para cerrar el layout al hacer clic en el botón de cerrar
    $('#closeLayout').on('click', function() {
        $('#bottomLayout').addClass('hidden');
    });

    // Función para reabrir el layout al hacer scroll
    $(window).on('scroll', function() {
        var scrollPos = $(window).scrollTop();
        if (scrollPos > 100) {  // Si haces scroll más de 100px, el layout permanece visible
            $('#bottomLayout').removeClass('hidden');
        } else {
            $('#bottomLayout').addClass('hidden');
        }
    });
});






document.addEventListener("DOMContentLoaded", () => {
    const dropdownButton = document.getElementById("dropdownButton");
    const dropdownMenu = document.getElementById("dropdownMenu");
    const dropdownContainer = document.getElementById("dropdownContainer");

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