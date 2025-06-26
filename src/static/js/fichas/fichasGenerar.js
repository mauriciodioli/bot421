$(document).ready(function() {
    $('#eliminarFichaForm').on('submit', function(event) {
        event.preventDefault(); // Evita el envío del formulario de manera tradicional
        
        // Captura los datos del formulario
        const accessToken = $('#access_token').val();
        const eliminarFichaId = $('#eliminarFichaId').val();
        const eliminarFichaCuenta = $('#eliminarFichaCuenta').val();
        const layoutOrigen = $('#layoutOrigen').val();

        // Realiza la solicitud AJAX
        $.ajax({
            url: '/eliminar-ficha', // Ruta del endpoint
            type: 'POST', // Método HTTP
            data: {
                access_token: accessToken,
                eliminarFichaId: eliminarFichaId,
                eliminarFichaCuenta: eliminarFichaCuenta,
                layoutOrigen: layoutOrigen
            },
            success: function(response) {
                // Maneja la respuesta del servidor
                if (response.mensaje) {
                    alert(response.mensaje); // Mensaje de éxito o error desde el servidor
                }
                
                if (response.fichas) {
                    // Actualizar la UI con los nuevos datos
                    actualizarTabla(response.fichas); // Accede a "fichas" dentro de "response"
                }

                // Cierra el modal
                $('#eliminarFichaModal').modal('hide');
            },
            error: function(xhr, status, error) {
                // Maneja errores
                console.error('Error en la solicitud:', error);
                alert('Ocurrió un error al eliminar la ficha.');
            }
        });
    });
});

function actualizarTabla(datos) {
    var tabla = document.getElementById('tablaDatos').getElementsByTagName('tbody')[0];  // Obtiene el cuerpo de la tabla

    // Limpiar la tabla si es necesario, o simplemente agregar nuevas filas
    tabla.innerHTML = ''; // Esto vacía el contenido actual de la tabla, opcional si deseas actualizar todo

    // Iterar sobre los datos recibidos y crear nuevas filas
    datos.forEach(function(ficha) {  // "datos" es ahora el array que contiene las fichas
        var nuevaFila = tabla.insertRow();  // Crear una nueva fila

        // Crear las celdas correspondientes para cada columna
        var celdaFicha = nuevaFila.insertCell(0);
        var celdaFecha = nuevaFila.insertCell(1);
        var celdaInicial = nuevaFila.insertCell(2);
        var celdaCapitalizacion = nuevaFila.insertCell(3);
        var celdaEstado = nuevaFila.insertCell(4);
        var celdaOperaciones = nuevaFila.insertCell(5);

        // Asignar el contenido a las celdas
        celdaFicha.innerHTML = ficha.id;
        celdaFecha.innerHTML = ficha.fecha_generacion;
        celdaInicial.innerHTML = ficha.monto_efectivo;
        celdaCapitalizacion.innerHTML = ficha.interes + "%";
        celdaEstado.innerHTML = ficha.estado;

        // Agregar botones en la celda de operaciones
        celdaOperaciones.innerHTML = `
            <button type="button" class="btn btn-danger mx-2" data-bs-toggle="modal" data-bs-target="#eliminarFichaModal" data-ficha-id="${ficha.id}" onclick="setFichaData(this.getAttribute('data-ficha-id'))" ${ficha.estado === 'ACEPTADO' ? 'disabled' : ''}>Eliminar</button>
            <button type="button" class="btn btn-success mx-2" data-bs-toggle="modal" data-bs-target="#tokenFichaModal" data-ficha-llave="${ficha.random_number}" data-ficha-monto="${ficha.monto_efectivo}" onclick="setFichaDataToken(this.getAttribute('data-ficha-llave'),this.getAttribute('data-ficha-monto'))" ${ficha.estado === 'ACEPTADO' ? 'disabled' : ''}><strong>TOKEN</strong></button>
        `;
    });
}
