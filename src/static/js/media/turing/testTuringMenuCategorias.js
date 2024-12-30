document.addEventListener('DOMContentLoaded', () => {
    const preguntasLista = document.getElementById('preguntas-lista');
    const categoriaMenu = document.getElementById('categoriaMenu');

    // Mostrar el menú de categorías
    function mostrarMenu(event) {
        const pregunta = event.target;
        const rect = pregunta.getBoundingClientRect();

        // Posicionar el menú cerca de la pregunta seleccionada
        categoriaMenu.style.display = 'block';
        categoriaMenu.style.top = `${rect.bottom + window.scrollY}px`;
        categoriaMenu.style.left = `${rect.left + window.scrollX}px`;

        // Guardar la pregunta seleccionada
        categoriaMenu.dataset.preguntaSeleccionada = pregunta.textContent;
    }

    // Seleccionar una categoría
    function seleccionarCategoria(event) {
        if (event.target && event.target.classList.contains('categoria-item')) {
            const categoria = event.target.dataset.categoria;
            const preguntaSeleccionada = categoriaMenu.dataset.preguntaSeleccionada;

            // Guardar la selección en localStorage           
            localStorage.setItem('seleccionCategoria', categoria);

            alert(`Seleccionaste la categoría "${categoria}" para la pregunta "${preguntaSeleccionada}".`);

            // Ocultar el menú
            cerrarMenu();
        }
    }

    // Cerrar el menú
    function cerrarMenu() {
        categoriaMenu.style.display = 'none';
    }

    // Manejar clics en las preguntas
    preguntasLista.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('pregunta-item')) {
            mostrarMenu(event);
        }
    });

    // Manejar clics en las categorías
    categoriaMenu.addEventListener('click', seleccionarCategoria);

    // Cerrar el menú si se hace clic fuera de él
    document.addEventListener('click', (event) => {
        if (!categoriaMenu.contains(event.target) && !preguntasLista.contains(event.target)) {
            cerrarMenu();
        }
    });



























    
});
