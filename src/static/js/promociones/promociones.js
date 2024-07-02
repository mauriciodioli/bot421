document.addEventListener('DOMContentLoaded', function() {
    // Datos a enviar
    const dataToSend = {
        access_token: localStorage.getItem('access_token'),
        correo_electronico: localStorage.getItem('correo_electronico')
    };

    // Enviar los datos por AJAX usando fetch
    fetch('/sistemaDePagos_get_promociones', {
        method: 'POST', // Método POST para enviar datos
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend) // Convertir datos a formato JSON
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        // Procesar la respuesta según sea necesario
        updateTablePromociones(data.promociones);
    })
    .catch(error => {
        console.error('Error al enviar datos por AJAX:', error);
    });
});


















document.addEventListener('DOMContentLoaded', function() {
    // Verifica si el elemento #enviarTablaBtn existe
    const enviarTablaBtn = document.getElementById('enviarTablaBtn');
    if (enviarTablaBtn) {
        // Agrega un event listener al hacer clic en el botón
        enviarTablaBtn.addEventListener('click', function() {
            const dataToSend = [];

            // Iterar sobre cada fila de la tabla #promocionesTabla
            document.querySelectorAll('#promocionesTabla tbody tr').forEach(function(row) {
                const rowData = {
                    idPlan: row.cells[0].textContent,
                    frecuencia: row.cells[1].textContent,
                    monto: row.cells[2].textContent,
                    descripcion: row.cells[3].textContent,
                    razon: row.cells[4].textContent,
                    moneda: row.cells[5].textContent,
                    meses: row.cells[7].textContent
                    // Agrega más propiedades según sea necesario
                };
                dataToSend.push(rowData);
            });

            // Enviar los datos por AJAX usando fetch
            fetch('/productosComerciales_promociones_agrega_promociones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Respuesta del servidor:', data);
                 // Procesar la respuesta según sea necesario
                 updateTablePromociones(data.promociones);
            })
            .catch(error => {
                console.error('Error al enviar datos por AJAX:', error);
            });
        });
    } else {
        console.error('El elemento #enviarTablaBtn no se encontró en el DOM.');
    }
});

function updateTablePromociones(promociones) {
    promocionesGlobal = promociones; // Hacer accesible promociones globalmente
    
    // Verificar si existe el elemento con ID promocionesTable
    const table = document.getElementById('promocionesTable');
    if (!table) {
         console.error('No se encontró el elemento con ID promocionesTable correcto control en Home');
        return;
    }

    const tableBody = table.getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    promociones.forEach(promocion => {
        const row = tableBody.insertRow();

        row.insertCell(0).textContent = promocion.id;
        row.insertCell(1).textContent = promocion.description;
        row.insertCell(2).textContent = promocion.price;
        row.insertCell(3).textContent = promocion.reason;
        row.insertCell(4).textContent = promocion.discount;
        row.insertCell(5).textContent = promocion.image_url;
        row.insertCell(6).textContent = promocion.state;
        row.insertCell(7).textContent = promocion.cluster;
        row.insertCell(8).textContent = promocion.currency_id;
        
        // Crear botón de modificar
        const modificarButton = document.createElement('button');
        modificarButton.textContent = 'Modificar';
        modificarButton.className = 'btn btn-success btn-sm modificar-promocion';
        modificarButton.setAttribute('data-id', promocion.id);

        // Crear botón de eliminar
        const eliminarButton = document.createElement('button');
        eliminarButton.textContent = 'Eliminar';
        eliminarButton.className = 'btn btn-danger btn-sm eliminar-promocion';
        eliminarButton.setAttribute('data-id', promocion.id);
        
        const cellAcciones = row.insertCell(9);
        cellAcciones.appendChild(modificarButton);
        cellAcciones.appendChild(eliminarButton);

        // Ocultar la primera columna (index 0, correspondiente a promocion.id)
        row.cells[0].style.display = 'none';
    });
}






























document.addEventListener('DOMContentLoaded', function() {
    $('#myModal').on('shown.bs.modal', function () {
        fetch('/productosComerciales_planes_muestra_planes/', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.planes) { // Verificar si data.planes existe en lugar de data.success
                console.log(data);
                updatePlanesTable(data.planes); // Llamar a la función de actualización con data.planes
            } else {
                console.error('Error en la respuesta del servidor:', data);
                alert('Error al cargar las planes');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar las planes');
        });
    });
});


function updatePlanesTable(planes) {
    planesGlobal = planes; // Hacer accesible planes globalmente
    
    // Verificar si existe el elemento con ID plansTable
    const table = document.getElementById('planesTable');
    if (!table) {
         console.error('No se encontró el elemento con ID plansTable correcto control en Home');
        return;
    }

    const tableBody = table.getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    planes.forEach(plan => {
        const row = tableBody.insertRow();

        row.insertCell(0).textContent = plan.id;
        row.insertCell(1).textContent = plan.frequency;
        row.insertCell(2).textContent = plan.amount;
        row.insertCell(3).textContent = plan.reason;
        row.insertCell(4).textContent = plan.frequency_type;
        row.insertCell(5).textContent = plan.currency_id;
        row.insertCell(6).textContent = plan.repetitions;
        row.insertCell(7).textContent = plan.billing_day;
        // Crear botón de modificar
        const modificarButton = document.createElement('button');
        modificarButton.textContent = 'Seleccionar';
        modificarButton.id = 'planesTable';
        modificarButton.className = 'btn btn-success btn-sm seleccionar-plan';
        // Puedes añadir un atributo data-* para guardar el ID u otra información relevante
        modificarButton.setAttribute('data-id', plan.id);
        
        
        const cellAcciones = row.insertCell(8);
        cellAcciones.appendChild(modificarButton);

        // Ocultar la primera columna (index 0, correspondiente a plan.frequency)
        row.cells[0].style.display = 'none';

      
    });
}


$(document).ready(function() {
    // Evento para seleccionar un plan
    $('#planesTable').on('click', '.seleccionar-plan', function() {
        // Obtener la fila de la tabla de planes
        var $row = $(this).closest('tr');
        var planData = [];
        
        // Obtener los datos de la fila
        $row.find('td').each(function() {
            planData.push($(this).text());
        });

        // Crear una nueva fila para la tabla de promociones
        var newRow = '<tr>';
        for (var i = 0; i < planData.length - 1; i++) { // Excluyendo el botón
            newRow += '<td>' + planData[i] + '</td>';
        }
        newRow += '<td><button class="btn btn-danger eliminar-promocion">Eliminar</button></td>';
        newRow += '</tr>';

        // Agregar la nueva fila a la tabla de promociones
        $('#promocionesTabla tbody').append(newRow);

        // Cerrar el modal
        $('#myModal').modal('hide');
    });

    // Evento para eliminar una promoción de la tabla de promociones
    $('#promocionesTabla').on('click', '.eliminar-promocion', function() {
        $(this).closest('tr').remove();
    });
});