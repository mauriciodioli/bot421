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
            debugger;
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








// Función para manejar la selección y el envío de datos
    // Seleccionamos el elemento con la clase "preguntaSeleccionada-item"
    const preguntaSeleccionada = document.querySelector('.preguntaSeleccionada-item');

    // Verificamos que el elemento exista
    if (preguntaSeleccionada) {
        // Agregamos un event listener al elemento para cuando sea clicado
        preguntaSeleccionada.addEventListener('click', (event) => {
            // Obtenemos los valores de los atributos data-preguntaSeleccionada y data-categoria
            const preguntaId = preguntaSeleccionada.getAttribute('data-preguntaSeleccionada');
            const categoriaId = preguntaSeleccionada.closest('.dropdown-menu')
                ?.querySelector('.categoria-item[data-categoria]')
                ?.getAttribute('data-categoria') || 'general'; // Predeterminamos "Todas" si no se seleccionó una categoría
            seleccionarCategoria(event) 
            // Construimos el objeto de datos a enviar
            const data = {
                preguntaId: preguntaId,
                categoriaId: categoriaId,
            };

            // Llamamos a la función para enviar los datos
           // enviarDatos('/turing-testTuring-obtener-respuestas-id/', data);
        });
    } else {
        console.warn('No se encontró el elemento .preguntaSeleccionada-item');
    }




// Función para enviar los datos mediante Fetch
function enviarDatos(url, data) {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // Especificamos que enviamos JSON
        },
        body: JSON.stringify(data) // Convertimos los datos a JSON
    })
        .then(response => {
            if (response.ok) {
                return response.json(); // Convertimos la respuesta a JSON
            } else {
                throw new Error('Error en la solicitud');
            }
        })
        .then(data => {
            console.log('Respuesta del servidor:', data);
        })
        .catch(error => {
            console.error('Hubo un problema con la solicitud:', error);
        });
}

















    
});
