document.addEventListener('DOMContentLoaded', function () {
    // Contenedor del menú desplegable
    const dropdownMenuContainer = document.querySelector('.custom-dropdown-menu-container');
    const dropdownMenu = document.querySelector('.custom-dropdown-menu');

    if (!dropdownMenuContainer || !dropdownMenu) {
        console.error("El contenedor o el menú desplegable no existe en el DOM.");
        return;
    }

    // Mostrar u ocultar el menú al hacer clic en el botón
    const closeLayoutBtn = dropdownMenuContainer.querySelector('.close-layout-btn');
    closeLayoutBtn.addEventListener('click', function () {
        dropdownMenu.style.display = dropdownMenu.style.display === 'none' || dropdownMenu.style.display === '' 
            ? 'flex' 
            : 'none';
    });

    // Delegación de eventos para manejar clics en los ítems del menú
    dropdownMenu.addEventListener('click', function (event) {
        const clickedElement = event.target;
       
        // Verificar si el clic ocurrió en un elemento del menú
        if (clickedElement.classList.contains('dropdown-item')) {
            event.preventDefault();
           
            const selectedItem = clickedElement.id; // ID del elemento clicado
            console.log(`Elemento seleccionado: ${selectedItem}`);

            // Guardar el ámbito seleccionado en localStorage
            localStorage.setItem('dominio', selectedItem);
          
            // Llamar a la función cargarPublicaciones (asegúrate de definir esta función previamente)
            //llamada desde js/media/muestraPublicacionesEnHome.js
            cargarPublicaciones(selectedItem, 'layout');
        }
    });

    // Función para cargar dinámicamente los ítems del menú desde el servidor
    window.cargarAmbitos = function ()  {
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
                const dropdownMenu = $('.custom-dropdown-menu'); // Usa jQuery para seleccionar el menú

                // Limpiar el menú existente
                dropdownMenu.empty();
                // Mapeo de íconos según el ámbito
                const iconosPorAmbito = {
                    "Personal": "👤",
                    "Laboral": "💼",
                    "Educacion": "📚",
                    "Negocios": "📈",
                    "Arte": "🎨",
                    "Deporte": "⚽",
                    "Social": "👥",
                    "Familia": "👨‍👩‍👧",
                    "Salud": "🏥",
                    "Animales": "🐶",
                    "Amistad": "🧑", // Ícono de una persona para Amistad
                    "Filantropia": "🤝", // Ícono para Filantropía
                    "Turismo": "✈️", // Ícono para Turismo                 
                    "Tecnología": "💻",
                    "Regionales": "🧉", // Ícono de mate para Regionales                   
                    "Work": "💼", // Laboral
                    "Education": "📚", // Educación
                    "Business": "📈", // Negocios
                    "Art": "🎨", // Arte
                    "Sports": "⚽", // Deporte
                    "Social": "👥", // Social
                    "Family": "👨‍👩‍👧", // Familia
                    "Health": "🏥", // Salud
                    "Pets": "🐶", // Animales
                    "Friendship": "🧑", // Amistad
                    "Philanthropy": "🤝", // Filantropía
                    "Tourism": "✈️", // Turismo
                    "Technology": "💻", // Tecnología
                    "Regional": "🧉" // Regionales
                };
              
                // Agregar los ámbitos dinámicamente al menú
                data.forEach(ambito => {                   
                    const icono = iconosPorAmbito[ambito.nombre] || ""; // Obtener el ícono correspondiente
                    const listItem = `
                        <li>
                            <a href="#" class="dropdown-item" id="${ambito.valor}">
                                ${icono} ${ambito.nombre}
                            </a>
                        </li>
                        <li><hr class="dropdown-divider"></li>
                    `;
                    dropdownMenu.append(listItem);
                });
                
                // Agregar el elemento "Turing test" al final del menú
                const turingTestItem = `
                <li class="nav-item content">
                    <a class="nav-link active" style="color: black;" href="/turing-testTuring">Turing test</a>
                </li>
                 <li><hr class="dropdown-divider"></li>
                `;
                dropdownMenu.append(turingTestItem);

                
                // Eliminar el último separador
                dropdownMenu.children('li').last().remove();
            })
            .catch(error => {
                console.error('Error al cargar los ámbitos:', error);
            });
    }

    // Cargar los ámbitos al cargar la página
    cargarAmbitos();
});











