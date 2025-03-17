function agregarEventListenerCategorias(ambitoId) {
    // Esperamos un pequeño tiempo para asegurarnos de que el DOM lo registre
    setTimeout(() => {
        const botonCategorias = document.getElementById(`caracteristicas-tab-${ambitoId}`);
        if (botonCategorias) {
            botonCategorias.addEventListener("click", function() {
                console.log(`Se hizo clic en Categorías del ámbito ${ambitoId}`);
                let nombreBandera = 'AcordeonAmbito' + ambitoId;
                debugger;
                let banderaActualizarCategoria = localStorage.getItem(nombreBandera);
                
                if (banderaActualizarCategoria !== null && banderaActualizarCategoria !== 'False') {
                  
                }else{
                    cargarAmbitosCategorias(ambitoId);
                }
                // Aquí puedes agregar la lógica que necesites
            });
        } else {
            console.warn(`No se encontró el botón Categorías para el ámbito ${ambitoId}`);
        }
      
        // Agregar evento a los elementos del dropdown para actualizar el color
        const categoriaItems = document.querySelectorAll(`#caracteristicas-tab-${ambitoId} .categoria-dropdown-item`);
        
        categoriaItems.forEach(item => {
            item.addEventListener('click', function() {
                const color = item.getAttribute('data-color');
                console.log(`Color seleccionado: ${color}`);
                
                // Actualizar el color del acordeón correspondiente
                updateColor(ambitoId, color);
            });
        });

    }, 100);
}


document.addEventListener('DOMContentLoaded', function () {
    // Seleccionamos el primer ítem que tiene el atributo 'data-color'
    debugger;
    const firstItem = document.querySelector('.categoria-dropdown-item[data-color]');
   
    // Si hay un primer ítem, actualizamos el color
    if (firstItem) {
        updateColor(firstItem);
    }

});

function updateColor(ambitoId, color) {
    // Asegúrate de que el ambitoId y color no sean nulos
    if (!ambitoId || !color) return;

    console.log(`Aplicando color: ${color} al acordeón con ambitoId: ${ambitoId}`);

    // Encuentra el acordeón y los elementos relevantes dentro de él
    const acordeonActivo = document.querySelector(`#acordeon-${ambitoId}`);
    const navTabs = acordeonActivo.querySelector('.nav-tabs');
    const homeTab = acordeonActivo.querySelector(`#home-tab-${ambitoId}`);
    const caracteristicasTab = acordeonActivo.querySelector(`#caracteristicas-tab-${ambitoId}`);

    // Eliminar clases de color anteriores
    ['border-red', 'border-green', 'border-blue', 'border-orange'].forEach(colorClass => {
        navTabs.classList.remove(colorClass);
        homeTab.classList.remove(colorClass);
        caracteristicasTab.classList.remove(colorClass);
    });

    // Aplicar nuevo color
    navTabs.classList.add(`border-${color}`);
    homeTab.classList.add(`border-${color}`);
    caracteristicasTab.classList.add(`border-${color}`);

    // Cambiar el color de texto del botón del dropdown si es necesario
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
    
        // Iterar sobre las categorías para cargar los elementos en el acordeón adecuado
        data.categorias.forEach(categoria => {
            // Encuentra el acordeón que tenga el ID correspondiente al ambitoId
            debugger;
                
            const acordeonActivo = document.querySelector(`#acordeon-${categoria.ambito}`);
            if (!acordeonActivo) return; // Si no encuentra el acordeón, salir
    
            // Buscar el contenedor adecuado dentro del acordeón activo
            const dropdownMenuCategorias = acordeonActivo.querySelector('.categoria-dropdown-menu');
            
            if (!dropdownMenuCategorias) {
                console.error('No se encontraron los elementos necesarios en el acordeón.');
                return;
            }
    
            // Limpiar el contenido solo una vez, fuera del forEach
            if (categoria === data.categorias[0]) {
                dropdownMenuCategorias.innerHTML = ''; // Limpiar el contenido antes de agregar los nuevos elementos
            }
    
            // Agregar los elementos del dropdown
            const color = categoria.color || 'orange';
    
            // Crear el item del dropdown
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
            nombreBandera = 'AcordeonAmbito'+categoria.ambito
            localStorage.setItem(nombreBandera, 'True');
            // Agregar el separador solo si no es el último elemento
            const index = data.categorias.indexOf(categoria);
            if (index < data.categorias.length - 1) {
                const divider = document.createElement('hr');
                divider.classList.add('dropdown-divider');
                dropdownMenuCategorias.appendChild(divider);
            }
        });
    })
    
    
    .catch(error => {
        console.error('Error al cargar las categorías:', error);
        alert('Hubo un problema al cargar las categorías. Inténtalo de nuevo.');
    });
}    

