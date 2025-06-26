
////////////////////////////////////////////////////////////////////////////
// Funciones para cargar las categorías de los ámbitos en el acordeón
////////////////////////////////////////////////////////////////////////////
function agregarEventListenerCategorias(ambitoId) {
    setTimeout(() => {
        const botonCategorias = document.getElementById(`caracteristicas-tab-${ambitoId}`);
       
        
        if (botonCategorias) {
            botonCategorias.addEventListener("click", function() {
                const actionElement = document.querySelector(`#acordeon-${ambitoId} .categoria-dropdown-menu .categoria-dropdown-item`);
               
                if (actionElement) {
                    console.log("Texto del elemento Action:", actionElement.textContent.trim());
                } else {
                    console.warn("No se encontró el elemento Action.");
                }
               
             
                if (actionElement.textContent.trim() === 'Action') {
                    cargarAmbitosCategorias(ambitoId);
                      // Elimina el elemento Action para que no vuelva a ser procesado
                    actionElement.remove();
                    console.log("Elemento Action eliminado.");
                   }
            });
        } else {
            console.warn(`No se encontró el botón Categorías para el ámbito ${ambitoId}`);
        }
    }, 100);
}

document.body.addEventListener('click', function(event) {
    // Verificamos si el elemento clickeado tiene la clase 'categoria-dropdown-item'
    if (event.target.classList.contains('categoria-dropdown-item')) {
        const categoriaValue = event.target.getAttribute('data-value');
        
        // Obtenemos el valor de 'data-color' y 'data-value' del elemento clickeado
        const color = event.target.getAttribute('data-color');
        const value = event.target.getAttribute('data-value');
         // Obtenemos el ambitoId de la parte del ID del div contenedor (navBar-Tecnologia)
        const ambitoId = event.target.closest('[id^="navBar-"]')?.id.replace('navBar-', '');
      
        if (ambitoId) {
            console.log(`Categoría seleccionada: ${value}, Color: ${color} para el ámbito ${ambitoId}`);
            const homeButton = document.querySelector(`#home-tab-${ambitoId}`);
            if (homeButton) {
                const categoriaValueSanitized = decodeURIComponent(categoriaValue);
                homeButton.textContent = categoriaValueSanitized; // Cambiar el texto del botón "Home"
            }
            updateColor(ambitoId, color);
            localStorage.setItem('categoria', categoriaValue);
            cargarPublicaciones(ambitoId);
        }
    }
});


////////////////////////////////////////////////////////////////////////////
function updateColor(ambitoId, color) {
    if (!ambitoId || !color) return;

    console.log(`Aplicando color: ${color} al acordeón con ambitoId: ${ambitoId}`);

    const acordeonActivo = document.querySelector(`#acordeon-${ambitoId}`);
    if (!acordeonActivo) return;

    const navTabs = acordeonActivo.querySelector('.nav-tabs');
    const homeTab = acordeonActivo.querySelector(`#home-tab-${ambitoId}`);
    const caracteristicasTab = acordeonActivo.querySelector(`#caracteristicas-tab-${ambitoId}`);

    if (!navTabs || !homeTab || !caracteristicasTab) return;

    ['border-red', 'border-green', 'border-blue', 'border-orange'].forEach(colorClass => {
        navTabs.classList.remove(colorClass);
        homeTab.classList.remove(colorClass);
        caracteristicasTab.classList.remove(colorClass);
    });

    navTabs.classList.add(`border-${color}`);
    homeTab.classList.add(`border-${color}`);
    caracteristicasTab.classList.add(`border-${color}`);
    caracteristicasTab.style.color = color;
}

function cargarAmbitosCategorias(ambito) {
    const cp = localStorage.getItem('codigoPostal') || '';
    if (ambito === 'inicialDominio') ambito = 'Laboral';

    const formData = new FormData();
    formData.append('ambito', ambito);
    if (cp) formData.append('cp', cp);

    fetch('/social-media-ambitosCategorias-categoria-mostrar/', {
        method: 'POST',
        body: formData,
        headers: { 'Accept': 'application/json' }
    })
    .then(response => response.json())
    .then(data => { 
        if (!data || !Array.isArray(data.categorias)) {
            throw new Error("La respuesta de la API no contiene 'categorias' o no es un array.");
        }

        const acordeonActivo = document.querySelector(`#acordeon-${ambito}`);
        if (!acordeonActivo) return;

        const dropdownMenuCategorias = acordeonActivo.querySelector('.categoria-dropdown-menu');
        if (!dropdownMenuCategorias) return;

        dropdownMenuCategorias.innerHTML = '';

        data.categorias.forEach(categoria => {
            const color = categoria.color || 'orange';

            const listItem = document.createElement('li');
            const link = document.createElement('a');

            link.href = "#";
            link.classList.add('dropdown-item', 'categoria-dropdown-item');
            link.id = categoria.id;
            link.dataset.value = categoria.valor;
            link.dataset.color = color;
            link.style.color = color;
            link.style.padding = "10px";
            link.textContent = categoria.nombre;

            listItem.appendChild(link);
            dropdownMenuCategorias.appendChild(listItem);
          
            if (categoria !== data.categorias[data.categorias.length - 1]) {
                const divider = document.createElement('hr');
                divider.classList.add('dropdown-divider');
                dropdownMenuCategorias.appendChild(divider);
            }
        });
    })
    .catch(error => {
        console.error('Error al cargar las categorías:', error);
    });
}
