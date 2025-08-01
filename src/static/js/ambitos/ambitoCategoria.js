$(document).ready(function() {
    $("#buscarAmbito").click(function() {
        let ambito = $("#ambitoInput").val();
        let cp = $("#codigoPostalInput").val();
      
        // Si los campos están vacíos, intentar recuperar desde localStorage
        if (!ambito) ambito = localStorage.getItem("dominio");
        if (!cp) cp = localStorage.getItem("codigoPostal");

        if (!ambito || !cp) {
            alert("Ingrese un ámbito y un código postal.");
            return;
        }

        $.ajax({
            url: "/social-media-ambitosCategorias-categoria-mostrar/",
            type: "POST",
            data: { ambito: ambito, cp: cp },
            contentType: 'application/x-www-form-urlencoded; charset=UTF-8',
            success: function(response) {
                if (response.categorias && response.categorias.length > 0) {
                    actualizarTabla(response.categorias);
                } else {
                    actualizarTabla([]); // Asegurar que se limpie la tabla
                    alert("No se encontraron categorías.");
                }
            },
            error: function() {
                alert("Error al obtener los datos.");
            }
        });
    });

    function actualizarTabla(datos) {
        let tbody = $("#tablaCategorias tbody");
        tbody.empty(); // Limpiar la tabla antes de agregar nuevos datos

        if (datos.length === 0) {
            tbody.append('<tr><td colspan="8" class="text-center">No hay datos disponibles</td></tr>');
        } else {
            $.each(datos, function(index, categoria) {
                let row = `<tr>
                    <td>${index + 1}</td>
                    <td>${categoria.id}</td>                  
                    <td>${categoria.nombre}</td>
                    <td>${categoria.descripcion}</td>
                    <td>${categoria.idioma}</td>
                    <td>${categoria.valor}</td>
                    <td>${categoria.color}</td>
                    <td>${categoria.estado}</td>
                    <td>
                        <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                        data-bs-target="#editarAmbitoCategoriaModal" 
                        data-ambitoCategoria-id="${categoria.id}"
                        data-nombre="${categoria.nombre}"
                        data-descripcion="${categoria.descripcion}"
                        data-idioma="${categoria.idioma}"
                        data-color="${categoria.color}"
                        data-valor="${categoria.valor}"
                        data-estado="${categoria.estado}">Editar</button>

                        <button type="button" class="btn btn-danger" data-bs-toggle="modal"
                            data-bs-target="#eliminarAmbitoCategoriaModal" 
                            data-ambitoCategoria-id="${categoria.id}"
                            data-nombre="${categoria.nombre}">Eliminar</button>
                    </td>
                </tr>`;
                tbody.append(row);
            });
        }
    }
});














function crearAmbitoCategorias() {
    let codigo_postal = document.getElementById("codigoPostalInput").value;
    let ambito = document.getElementById("ambitoInput").value;
    if (!ambito || !codigo_postal) {
        ambito = localStorage.getItem("dominio");
        codigo_postal = localStorage.getItem("codigoPostal");
    }
    // Obtener los valores del formulario
    let nombre = document.getElementById("nombre").value;
    let descripcion = document.getElementById("descripcion").value;
    let idioma = document.getElementById("idioma").value;
    let valor = document.getElementById("valor").value;
    let color = document.getElementById("color").value;
    let estado = document.getElementById("estado").value;
   
    // Validar campos obligatorios
    if (!nombre || !descripcion||!idioma||!valor||!color||!estado) {
        alert("Los campos 'Nombre' 'color', 'Idioma', 'Valor', 'Estado' y 'Descripción' son obligatorios.");
        return;
    }

    // Crear el objeto de datos
    let datos = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        color: color,
        ambito: ambito,
        estado: estado,
        cp: codigo_postal
    };

    // Enviar la solicitud AJAX
    fetch('/social-media-ambitos-crear-categoria/', {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(datos)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Error: " + data.error);
        } else {
            alert("Categoría creada exitosamente.");
            agregarFilaATabla(data); // Llamar función para actualizar la tabla
            document.getElementById("ambitoCategoria-form").reset(); // Limpiar formulario
        }
    })
    .catch(error => console.error("Error:", error));
}

function agregarFilaATabla(data) {
    let tabla = document.querySelector("table tbody");
    let fila = document.createElement("tr");

    fila.innerHTML = `
        <td>#</td>
        <td>${data.id}</td>      
        <td>${data.nombre}</td>
        <td>${data.descripcion}</td>
        <td>${data.idioma}</td>       
        <td>${data.valor}</td>
        <td>${data.color}</td>
        <td>${data.estado}</td>
        <td>
            <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                data-bs-target="#editarAmbitoModal"                 
                data-ambitoCategoria-id="${data.id}"
                data-nombre="${data.nombre}"
                data-descripcion="${data.descripcion}"
                data-idioma="${data.idioma}"
                data-valor="${data.valor}"
                data-color="${data.color}"
                data-estado="${data.estado}">
                Editar
            </button>
            <button type="button" class="btn btn-danger" data-bs-toggle="modal"
                data-bs-target="#eliminarAmbitoCategoriaModal" 
                data-ambitoCategoria-id="${data.id}"
                data-nombre="${data.nombre}">
                Eliminar
            </button>
        </td>
    `;
    tabla.appendChild(fila);
}



// Función para actualizar un ambitoCategoria
function actualizarAmbitoCategoria() {
    const id = document.getElementById('AmbitoCategoria-id-editar').value;
    const nombre = document.getElementById('nombre-editar').value;
    const descripcion = document.getElementById('descripcion-editar').value;
    const idioma = document.getElementById('idioma-editar').value;
    const valor = document.getElementById('valor-editar').value;
    const color = document.getElementById('color-editar').value;
    const estado = document.getElementById('estado-editar').value;
    const userId = document.getElementById('user_id-editar').value;
   
    const data = {
        nombre: nombre,
        descripcion: descripcion,
        idioma: idioma,
        valor: valor,
        color: color,
        estado: estado,
        user_id: userId
    };
    
    fetch(`/social-media-ambitos-actualizar-categoria/${id}`, {  // ✅ Ruta corregida
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {       
        alert('Ámbito actualizado con éxito');
        $('#editarAmbitoCategoriaModal').modal('hide'); // Cerrar el modal
        obtenerAmbitosCategoria();  // Actualizar la lista de ámbitos
    })
    .catch(error => {
        alert('Error al actualizar el ámbito: ' + error);
    });
}


obtenerAmbitosCategoria(); // Llamar a la función para cargar los ámbitos al inicio

// Función para obtener todos los ambitosCategorias
function obtenerAmbitosCategoria() {
    let ambito = localStorage.getItem("dominio") || "";
    let cp = localStorage.getItem("codigoPostal") || "";

    $.ajax({
        url: "/social-media-publicaciones-obtener-ambitosCategorias/",
        type: "POST",  // Si tu API permite GET, cámbialo a "GET"
        data: JSON.stringify({ ambito: ambito, cp: cp }),
        contentType: "application/json",
    })
    .done(function(response) { // Correcto uso de jQuery
        if (!response || response.length === 0) {
            const tablaCuerpo = document.querySelector('table tbody');
            tablaCuerpo.innerHTML = '<tr><td colspan="9" class="text-center">No hay datos disponibles</td></tr>';
            return;
        }

        const iconosPorAmbito = {
            "Personal": "👤", "Laboral": "💼", "Educacion": "📚",
            "Negocios": "📈", "Arte": "🎨", "Deporte": "⚽",
            "Social": "👥", "Familia": "👨‍👩‍👧", "Salud": "🏥",
            "Animales": "🐶", "Amistad": "🧑", "Filantropia": "🤝",
            "Turismo": "✈️", "Tecnología": "💻", "Regionales": "🧉",
            "Work": "💼", "Education": "📚", "Business": "📈",
            "Art": "🎨", "Sports": "⚽", "Social": "👥",
            "Family": "👨‍👩‍👧", "Health": "🏥", "Pets": "🐶",
            "Friendship": "🧑", "Philanthropy": "🤝", "Tourism": "✈️",
            "Technology": "💻", "Regional": "🧉"
        };

        const tablaCuerpo = document.querySelector('table tbody');
        tablaCuerpo.innerHTML = ''; // Limpiar la tabla antes de agregar nuevos elementos

        response.forEach((categoria, index) => {
            const icono = iconosPorAmbito[categoria.nombre] || ""; // Obtener el ícono correspondiente
            const tr = document.createElement('tr');
            console.log(categoria);
            tr.innerHTML = `
                <td>${index + 1}</td>                   
                <td>${categoria.id}</td>
                <td>${categoria.nombre}</td>
                <td>${categoria.descripcion}</td>
                <td>${categoria.idioma}</td>
                <td>${icono} ${categoria.valor}</td>
                <td>${categoria.color}</td>
                <td>${categoria.estado}</td>
                <td>
                    <button type="button" class="btn btn-primary" data-bs-toggle="modal"
                        data-bs-target="#editarAmbitoModal"
                        data-categoria-id="${categoria.id}"
                        data-nombre="${categoria.nombre}"
                        data-descripcion="${categoria.descripcion}"
                        data-idioma="${categoria.idioma}"
                        data-valor="${categoria.valor}"
                        data-color="${categoria.color}"
                        data-estado="${categoria.estado}"
                        data-user_id="${categoria.user_id}">Editar</button>
                    <button type="button" class="btn btn-danger" data-bs-toggle="modal"
                        data-bs-target="#eliminarAmbitoCategoriaModal"
                        data-categoria-id="${categoria.id}"
                        data-nombre="${categoria.nombre}">Eliminar</button>
                </td>
            `;
            tablaCuerpo.appendChild(tr);
        });
    })
    .fail(function(error) {
        alert('Error al obtener los ámbitos: ' + error.responseText);
    });
}








// Función para eliminar un ámbito por ID
function  eliminarAmbitoCategoria(id) {
    
    fetch(`/social-media-publicaciones-ambitosCategorias-delete/${id}`, {
        method: 'DELETE'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        alert('Ámbito eliminado con éxito');
        $('#eliminarAmbitoCategoriaModal').modal('hide'); // Cerrar el modal
        obtenerAmbitosCategoria(); // Actualizar la lista de ámbitos
    })
    .catch(error => {
        alert('Error al eliminar el ámbito: ' + error.message);
    });
}
