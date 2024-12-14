// Función para manejar la acción dependiendo del tipo
function accionAmbito(accion) {
    switch (accion) {
        case 'alta':
            // Llamar la función para crear un nuevo ambito
            crearAmbito();
            break;
        case 'baja':
            // Llamar la función para eliminar un ambito
            const idBaja = prompt("Ingrese el ID del ambito a eliminar:");
            eliminarAmbito(idBaja);
            break;
        case 'modificacion':
            // Llamar la función para modificar un ambito
            const idMod = prompt("Ingrese el ID del ambito a modificar:");
            obtenerAmbito(idMod);  // Obtiene los detalles del ambito para editarlo
            break;
        case 'consulta':
            // Llamar la función para consultar un ambito
            const idConsulta = prompt("Ingrese el ID del ambito a consultar:");
            obtenerAmbito(idConsulta);  // Obtiene los detalles del ambito para verlos
            break;
        default:
            alert("Acción no válida");
            break;
    }
}

// Función para crear un nuevo ambito
function crearAmbito() {
    const nombre = document.getElementById('nombre').value;
    const descripcion = document.getElementById('descripcion').value;
    const idioma = document.getElementById('idioma').value;
    const valor = document.getElementById('valor').value;
    const estado = document.getElementById('estado').value;
    const userId = document.getElementById('user_id').value;

    const data = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        estado: estado,
        user_id: userId
    };

    fetch('/social-media-publicaciones-ambitos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert('Ambito creado con éxito');
        obtenerAmbitos();  // Actualizar la lista de ambitos
    })
    .catch(error => {
        alert('Error al crear el ambito: ' + error);
    });
}

// Función para obtener todos los ambitos
function obtenerAmbitos() {
    fetch('/social-media-publicaciones-ambitos')
        .then(response => response.json())
        .then(data => {
            const ambitosList = document.getElementById('ambitos-list');
            ambitosList.innerHTML = '';  // Limpiar lista antes de agregar
            data.forEach(ambito => {
                const li = document.createElement('li');
                li.textContent = `${ambito.nombre} - ${ambito.descripcion}`;
                li.setAttribute('data-id', ambito.id);
                li.addEventListener('click', () => obtenerAmbito(ambito.id));  // Ver detalles
                ambitosList.appendChild(li);
            });
        })
        .catch(error => {
            alert('Error al obtener los ambitos: ' + error);
        });
}

// Función para obtener un ambito por ID
function obtenerAmbito(id) {
    fetch(`/social-media-publicaciones-ambitos/${id}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('nombre').value = data.nombre;
            document.getElementById('descripcion').value = data.descripcion;
            document.getElementById('idioma').value = data.idioma;
            document.getElementById('valor').value = data.valor;
            document.getElementById('estado').value = data.estado;
            document.getElementById('user_id').value = data.user_id;
            document.getElementById('ambito-id').value = data.id;  // ID para actualización
        })
        .catch(error => {
            alert('Error al obtener el ambito: ' + error);
        });
}

// Función para actualizar un ambito
function actualizarAmbito() {
    const id = document.getElementById('ambito-id').value;
    const nombre = document.getElementById('nombre').value;
    const descripcion = document.getElementById('descripcion').value;
    const idioma = document.getElementById('idioma').value;
    const valor = document.getElementById('valor').value;
    const estado = document.getElementById('estado').value;
    const userId = document.getElementById('user_id').value;

    const data = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        estado: estado,
        user_id: userId
    };

    fetch(`/social-media-publicaciones-ambitos/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        alert('Ambito actualizado con éxito');
        obtenerAmbitos();  // Actualizar la lista de ambitos
    })
    .catch(error => {
        alert('Error al actualizar el ambito: ' + error);
    });
}

// Función para eliminar un ambito por ID
function eliminarAmbito(id) {
    fetch(`/social-media-publicaciones-ambitos/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        alert('Ambito eliminado con éxito');
        obtenerAmbitos();  // Actualizar la lista de ambitos
    })
    .catch(error => {
        alert('Error al eliminar el ambito: ' + error);
    });
}

// Ejecutar al cargar la página
window.onload = function() {
    obtenerAmbitos();
};
