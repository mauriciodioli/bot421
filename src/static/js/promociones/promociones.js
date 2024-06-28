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
       
        row.insertCell(8).appendChild(modificarButton);

      
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