document.addEventListener('DOMContentLoaded', function () {
    const ambitoSelects = [
        document.getElementById('postAmbito_creaPublicacion'),
        document.getElementById('postAmbito_modificaPublicacion')
    ]; // Selects donde cargar los ámbitos

    const dropdownMenu = document.querySelector('.custom-dropdown-menu'); // Dropdown dinámico

    // Verificar que todos los elementos necesarios existan
    if (ambitoSelects.some(select => !select) || !dropdownMenu) {
        console.error("Uno o más elementos necesarios no existen en el DOM.");
        return;
    }

    // Función para cargar los ámbitos desde el servidor
    window.cargarAmbitos = function () {
        fetch('/social-media-publicaciones-obtener-ambitos/', {
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
            // Actualizar selects
            ambitoSelects.forEach(select => {
                select.innerHTML = '<option value="" disabled selected>Selecciona un ámbito</option>';
                data.forEach(ambito => {
                    const option = document.createElement('option');
                    option.value = ambito.valor;
                    option.textContent = ambito.nombre;
                    select.appendChild(option);
                });
            });
            
            // Actualizar menú desplegable
            dropdownMenu.innerHTML = ''; // Limpiar contenido existente
            data.forEach(ambito => {
                const listItem = `
                    <li>
                        <a class="dropdown-item" id="${ambito.valor}" href="#" data-val="${ambito.valor}">
                            ${ambito.nombre}
                        </a>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                `;
                dropdownMenu.insertAdjacentHTML('beforeend', listItem);
            });

            // Eliminar el último separador del menú
            const lastDivider = dropdownMenu.querySelector('li:last-child');
            if (lastDivider) {
                lastDivider.remove();
            }

            // Asignar eventos a los nuevos elementos del menú
            agregarEventosClick();

            // 🔥 NUEVO: si hay al menos un ámbito, auto-seleccionar el primero y disparar 'change'
            if (data.length > 0) {
                const firstAmbitoValor = data[0].valor;

                ambitoSelects.forEach(select => {
                    if (select) {
                        select.value = firstAmbitoValor;
                        // dispara el change para que el otro JS cargue las categorías
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });

                // Opcional: también cargar publicaciones del primer ámbito
                if (typeof cargarPublicaciones === 'function') {
                    cargarPublicaciones(firstAmbitoValor);
                }
            }
        })
        .catch(error => {
            console.error('Error al cargar los ámbitos:', error);
        });
    };

    // Función para asignar eventos a los elementos del menú
    function agregarEventosClick() {
        const menuItems = document.querySelectorAll('.dropdown-item');
        menuItems.forEach(item => {
            item.addEventListener('click', function (event) {
                event.preventDefault();
                const ambitoId = this.dataset.val; // Obtener el valor dinámico del ámbito seleccionado

                // 🔥 NUEVO: sincronizar selects y disparar 'change' → carga categorías
                ambitoSelects.forEach(select => {
                    if (select) {
                        select.value = ambitoId;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });

                // Llamar a la función que maneja la lógica del acordeón (ya la tenías)
                cargarPublicaciones(ambitoId);
            });
        });
    }

    // Llamar a la función para cargar los ámbitos al cargar la página
    cargarAmbitos();
});
