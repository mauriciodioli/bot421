document.addEventListener('DOMContentLoaded', function () {
    
    // Obtener los selects de ámbitos y categorías para creación y modificación
    const ambitoSelects = {

        crea: document.getElementById('postAmbito_creaPublicacion'),
        modifica: document.getElementById('postAmbito_modificaPublicacion')
    };

    const categoriaSelects = {
        crea: document.getElementById('postAmbitoCategorias_creaPublicacion'),
        modifica: document.getElementById('postAmbitoCategorias_modificaPublicacion')
    };

    // Función para cargar categorías según el ámbito seleccionado
    function cargarCategorias(ambitoSelect, categoriaSelect) {
        const ambitoSeleccionado = ambitoSelect.value;

        if (!ambitoSeleccionado) {
            console.warn("Ningún ámbito seleccionado.");
            return;
        }
        cp = localStorage.getItem('codigoPostal');

        fetch('/social-media-publicaciones-obtener-ambitosCategorias/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ambito: ambitoSeleccionado,cp: cp })
        })
        .then(response => {
            if (!response.ok) throw new Error('Error al obtener las categorías.');
            return response.json();
        })
        .then(data => {
       
            categoriaSelect.innerHTML = '<option value="" disabled selected>Selecciona una categoría</option>';
            data.forEach(categoria => {
                const option = document.createElement('option');
                option.value = categoria.id;  // Suponiendo que el ID viene en la respuesta
              
                option.textContent = categoria.nombre;
                categoriaSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Error al cargar las categorías:", error);
        });
    }

    // Asignar evento 'change' a los selects de ámbito
    Object.keys(ambitoSelects).forEach(key => {
        if (ambitoSelects[key] && categoriaSelects[key]) {
            ambitoSelects[key].addEventListener('change', function () {
                cargarCategorias(ambitoSelects[key], categoriaSelects[key]);
            });
        }
    });
});
