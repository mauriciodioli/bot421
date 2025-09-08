// Función para mostrar el modal de confirmación
function crearAmbito() {
    
    // Primero muestra el modal de confirmación
    $('#confirmacionCrearAmbitoModal').modal('show');
}



// Función para crear un nuevo ámbito
function confirmarCrearAmbito() {
    
    const nombre = document.getElementById('nombre').value;
    const descripcion = document.getElementById('descripcion').value;
    const idioma = document.getElementById('idioma').value;
    const valor = document.getElementById('valor').value;
    const estado = document.getElementById('estado').value;
    const userId = localStorage.getItem('usuario_id');

    // Validar los campos obligatorios
    if (!nombre || !descripcion || !userId) {
        alert('Por favor, completa los campos requeridos.');
        return;
    }
  
    const data = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        estado: estado,
        user_id: userId
    };
    

    // Realizar la solicitud al servidor para crear el ámbito
    fetch('/social-media-publicaciones-ambitos-crear/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        
        $('#confirmacionCrearAmbitoModal').modal('hide'); // Cerrar el modal
        alert('Ámbito creado con éxito');
        obtenerAmbitos();  // Actualizar la lista de ámbitos
       
    })
    .catch(error => {
        alert('Error al crear el ámbito: ' + error);
        modal.style.display = "none";  // Ocultar el modal en caso de error
    });

}
// Función para obtener todos los ambitos
function obtenerAmbitos() {
    
    fetch('/social-media-publicaciones-obtener-ambitos/')
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error del servidor: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
             
            const tablaCuerpo = document.querySelector('table tbody');

            // Limpiar filas existentes (incluidas las renderizadas por Jinja)
            tablaCuerpo.innerHTML = '';

            if (data.length === 0) {
                // Si no hay datos, mostrar mensaje en la tabla
                tablaCuerpo.innerHTML = '<tr><td colspan="9" class="text-center">No hay datos disponibles</td></tr>';
                return;
            }
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
            data.forEach((ambito, index) => {
                const icono = iconosPorAmbito[ambito.nombre] || ""; // Obtener el ícono correspondiente
                const tr = document.createElement('tr');

                // Crear las celdas dinámicamente
                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${ambito.id}</td>
                    <td>${ambito.user_id}</td>
                    <td>${ambito.nombre}</td>
                    <td>${ambito.descripcion}</td>
                    <td>${ambito.idioma}</td>
                    <td>${icono} ${ambito.valor}</td>
                    <td>${ambito.estado}</td>
                    <td>
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                            data-bs-target="#editarAmbitoModal"
                            data-ambito-id="${ambito.id}"
                            data-nombre="${ambito.nombre}"
                            data-descripcion="${ambito.descripcion}"
                            data-idioma="${ambito.idioma}"
                            data-valor="${ambito.valor}"
                            data-estado="${ambito.estado}"
                            data-user_id="${ambito.user_id}">Editar</button>
                        <button type="button" class="btn btn-danger" data-bs-toggle="modal"
                            data-bs-target="#eliminarAmbitoModal"
                            data-ambito-id="${ambito.id}"
                            data-nombre="${ambito.nombre}">Eliminar</button>
                    </td>
                `;
                tablaCuerpo.appendChild(tr);
            });
        })
        .catch(error => {
            alert('Error al obtener los ámbitos: ' + error.message);
        });
}

// Función para obtener un ambito por ID
function obtenerAmbito_por_id(id) {
    fetch(`/social-media-publicaciones-ambitos-obtener-por-id/${id}`)
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
   
    const id = document.getElementById('ambito-id-editar').value;
    const nombre = document.getElementById('nombre-editar').value;
    const descripcion = document.getElementById('descripcion-editar').value;
    const idioma = document.getElementById('idioma-editar').value;
    const valor = document.getElementById('valor-editar').value;
    const estado = document.getElementById('estado-editar').value;
    const userId = document.getElementById('user_id-editar').value;
    const codigoPostal = document.getElementById('codigo_postal-editar').value;


    const data = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        estado: estado,
        user_id: userId
    };
    
    fetch(`/social-media-publicaciones-ambitos-actualizar/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {       
        alert('Ambito actualizado con éxito');
        $('#editarAmbitoModal').modal('hide'); // Cerrar el modal
        obtenerAmbitos();  // Actualizar la lista de ambitos
    })
    .catch(error => {
        alert('Error al actualizar el ambito: ' + error);
    });
}

// Función para eliminar un ambito por ID
function eliminarAmbito(id) {
    
    fetch(`/social-media-publicaciones-ambitos-delete/${id}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) { // Verifica si hay un mensaje de éxito
            alert('Ámbito eliminado con éxito');
            $('#eliminarAmbitoModal').modal('hide'); // Cerrar el modal
            obtenerAmbitos(); // Actualizar la lista de ámbitos
        } else {
            alert('Error al eliminar el ámbito: ' + (data.error || 'Respuesta inesperada'));
        }
    })
    .catch(error => {
        alert('Error al eliminar el ámbito: ' + error);
    });
}
















function actualizarAmbitoCambiarPosicion() {
    const id_1 = document.getElementById('id-ambito-uno').value;
    const id_2 = document.getElementById('id-ambito-dos').value;

    const data = {
        id_1: id_1,
        id_2: id_2       
    };

    fetch(`/social-media-publicaciones-ambitos-cambiarPosicion/${id_1}/${id_2}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {       
        alert('Ámbito actualizado con éxito');
        $('#editarAmbitoModal').modal('hide'); // Cerrar el modal
        obtenerAmbitos();  // Actualizar la lista de ámbitos
    })
    .catch(error => {
        alert('Error al actualizar el ámbito: ' + error);
    });
}




