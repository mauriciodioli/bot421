<<<<<<< HEAD
document.addEventListener('DOMContentLoaded', function() {
    fetchPromocionesSinPlan();
    fetchPromociones();
    setupEnviarTablaBtn();
    setupSavePromotionBtn();
});

function fetchPromocionesSinPlan() {
    $('#savePromotionBtnAgregarPromocion').click(function() {
        const promotionData = {
            precio: $('#promotionPrice1').val(),
            descripcion: $('#promotionDescription1').val(),
            descuento: $('#promotionDiscount1').val(),
            razon: $('#promotionReason1').val(),
            estado: $('#promotionStatus1').val(),
            moneda: $('#promotionCurrency1').val(),
            cluster: $('#promotionCluster1').val()
        };

        $.ajax({
            url: '/productosComerciales_promociones_agrega_promocionesSinPlan',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(promotionData),
            success: function(response) {
                alert('Promoción agregada exitosamente');
                $('#modalAgregarPromocionSinPlan').modal('hide');
                fetchPromociones(); // Refresh the table after adding
            },
            error: function(error) {
                alert('Error al agregar promoción');
            }
        });
    });
}

function fetchPromociones() {
    const dataToSend = {
        access_token: localStorage.getItem('access_token'),
        correo_electronico: localStorage.getItem('correo_electronico')
    };

    fetch('/sistemaDePagos_get_promociones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        updateTablePromociones(data.promociones);
    })
    .catch(error => {
        console.error('Error al enviar datos por AJAX:', error);
    });
}

function setupEnviarTablaBtn() {
    const enviarTablaBtn = document.getElementById('enviarTablaBtn');
    if (enviarTablaBtn) {
        enviarTablaBtn.addEventListener('click', function() {
            const dataToSend = [];

            document.querySelectorAll('#promocionesTabla tbody tr').forEach(function(row) {
                const rowData = {
                    id: row.cells[0].textContent,
                    frecuencia: row.cells[1].textContent,
                    monto: row.cells[2].textContent,
                    descripcion: row.cells[3].textContent,
                    razon: row.cells[4].textContent,
                    moneda: row.cells[5].textContent,
                    meses: row.cells[7].textContent
                };
                dataToSend.push(rowData);
            });

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
                updateTablePromociones(data.promociones);
                alert('Promoción agregada con éxito.');
            })
            .catch(error => {
                console.error('Error al enviar datos por AJAX:', error);
            });
        });
    } else {
        console.error('El elemento #enviarTablaBtn no se encontró en el DOM.');
    }
}

function setupSavePromotionBtn() {
    $('#savePromotionBtnModificaPromocion').click(function() {
        const promotionData = {
            id: $('#promotionId').val(),
            precio: $('#promotionPrice').val(),
            descripcion: $('#promotionDescription').val(),
            descuento: $('#promotionDiscount').val(),
            razon: $('#promotionReason').val(),
            estado: $('#promotionStatus').val(),
            moneda: $('#promotionCurrency').val(),
            cluster: $('#promotionCluster').val()
        };

        $.ajax({
            url: '/productosComerciales_promociones_modifica_promocionesSinPlan',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(promotionData),
            success: function(response) {
                alert('Promoción modificada exitosamente');
                $('#modalModificaPromocion').modal('hide');
                fetchPromociones(); // Refresh the table after modification
            },
            error: function(error) {
                alert('Error al modificar promoción');
            }
        });
    });
}

function updateTablePromociones(promociones) {
    const table = document.getElementById('promocionesTable');
    if (!table) {
        console.error('No se encontró el elemento con ID promocionesTable.');
        return;
    }

    const tableBody = table.getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    promociones.forEach(promocion => {
        const row = tableBody.insertRow();

        row.insertCell(0).textContent = promocion.id;
        row.insertCell(1).textContent = promocion.price;
        row.insertCell(2).textContent = promocion.description;
        row.insertCell(3).textContent = promocion.discount;
        row.insertCell(4).textContent = promocion.reason;
        row.insertCell(5).textContent = promocion.state;
        row.insertCell(6).textContent = promocion.cluster;
        row.insertCell(7).textContent = promocion.currency_id;

        const modificarButton = document.createElement('button');
        modificarButton.textContent = 'Modificar';
        modificarButton.className = 'btn btn-success btn-sm modificar-promocion';
        modificarButton.setAttribute('data-id', promocion.id);

        const eliminarButton = document.createElement('button');
        eliminarButton.textContent = 'Eliminar';
        eliminarButton.className = 'btn btn-danger btn-sm eliminar-promocion';
        eliminarButton.setAttribute('data-id', promocion.id);

        const cellAcciones = row.insertCell(8);
        cellAcciones.appendChild(modificarButton);
        cellAcciones.appendChild(eliminarButton);
       // row.cells[0].style.display = 'none';
    });

    setupModificarButtons(promociones);
    setupEliminarButtons();
}

function setupModificarButtons(promociones) {
    document.querySelectorAll('.modificar-promocion').forEach(button => {
        button.addEventListener('click', (event) => {
            const id = event.target.getAttribute('data-id');
            const promocion = promociones.find(promo => promo.id == id);
            if (promocion) { 
                
                document.getElementById('promotionId').value = promocion.id; 
                document.getElementById('promotionPrice').value = promocion.price;
                document.getElementById('promotionDescription').value = promocion.description;
                document.getElementById('promotionDiscount').value = promocion.discount;
                document.getElementById('promotionReason').value = promocion.reason;
                document.getElementById('promotionStatus').value = promocion.state;
                document.getElementById('promotionCurrency').value = promocion.currency_id;
                document.getElementById('promotionCluster').value = promocion.cluster;

                const modal = new bootstrap.Modal(document.getElementById('modalModificaPromocion'));
                modal.show();
            }
        });
    });
}

function setupEliminarButtons() {
    document.querySelectorAll('.eliminar-promocion').forEach(button => {
        button.addEventListener('click', (event) => {
            const id = event.target.getAttribute('data-id');
            const data = { id: id };

            fetch('/productosComerciales_promociones_elimina_promociones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    updateTablePromociones(data.promociones);
                    alert('Promoción eliminada con éxito.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
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
             
            }
        })
        .catch(error => {
            console.error('Error:', error);
           
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
=======
document.addEventListener('DOMContentLoaded', function() {
    fetchPromocionesSinPlan();
    fetchPromociones();
    setupEnviarTablaBtn();
    setupSavePromotionBtn();
});

function fetchPromocionesSinPlan() {
    $('#savePromotionBtnAgregarPromocion').click(function() {
        const promotionData = {
            precio: $('#promotionPrice1').val(),
            descripcion: $('#promotionDescription1').val(),
            descuento: $('#promotionDiscount1').val(),
            razon: $('#promotionReason1').val(),
            estado: $('#promotionStatus1').val(),
            moneda: $('#promotionCurrency1').val(),
            cluster: $('#promotionCluster1').val()
        };

        $.ajax({
            url: '/productosComerciales_promociones_agrega_promocionesSinPlan',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(promotionData),
            success: function(response) {
                alert('Promoción agregada exitosamente');
                $('#modalAgregarPromocionSinPlan').modal('hide');
                fetchPromociones(); // Refresh the table after adding
            },
            error: function(error) {
                alert('Error al agregar promoción');
            }
        });
    });
}

function fetchPromociones() {
    const dataToSend = {
        access_token: localStorage.getItem('access_token'),
        correo_electronico: localStorage.getItem('correo_electronico')
    };

    fetch('/sistemaDePagos_get_promociones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(dataToSend)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Respuesta del servidor:', data);
        updateTablePromociones(data.promociones);
    })
    .catch(error => {
        console.error('Error al enviar datos por AJAX:', error);
    });
}

function setupEnviarTablaBtn() {
    const enviarTablaBtn = document.getElementById('enviarTablaBtn');
    if (enviarTablaBtn) {
        enviarTablaBtn.addEventListener('click', function() {
            const dataToSend = [];

            document.querySelectorAll('#promocionesTabla tbody tr').forEach(function(row) {
                const rowData = {
                    id: row.cells[0].textContent,
                    frecuencia: row.cells[1].textContent,
                    monto: row.cells[2].textContent,
                    descripcion: row.cells[3].textContent,
                    razon: row.cells[4].textContent,
                    moneda: row.cells[5].textContent,
                    meses: row.cells[7].textContent
                };
                dataToSend.push(rowData);
            });

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
                updateTablePromociones(data.promociones);
                alert('Promoción agregada con éxito.');
            })
            .catch(error => {
                console.error('Error al enviar datos por AJAX:', error);
            });
        });
    } else {
        console.error('El elemento #enviarTablaBtn no se encontró en el DOM.');
    }
}

function setupSavePromotionBtn() {
    $('#savePromotionBtnModificaPromocion').click(function() {
        const promotionData = {
            id: $('#promotionId').val(),
            precio: $('#promotionPrice').val(),
            descripcion: $('#promotionDescription').val(),
            descuento: $('#promotionDiscount').val(),
            razon: $('#promotionReason').val(),
            estado: $('#promotionStatus').val(),
            moneda: $('#promotionCurrency').val(),
            cluster: $('#promotionCluster').val()
        };

        $.ajax({
            url: '/productosComerciales_promociones_modifica_promocionesSinPlan',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(promotionData),
            success: function(response) {
                alert('Promoción modificada exitosamente');
                $('#modalModificaPromocion').modal('hide');
                fetchPromociones(); // Refresh the table after modification
            },
            error: function(error) {
                alert('Error al modificar promoción');
            }
        });
    });
}

function updateTablePromociones(promociones) {
    const table = document.getElementById('promocionesTable');
    if (!table) {
        console.error('No se encontró el elemento con ID promocionesTable.');
        return;
    }

    const tableBody = table.getElementsByTagName('tbody')[0];
    tableBody.innerHTML = '';

    promociones.forEach(promocion => {
        const row = tableBody.insertRow();

        row.insertCell(0).textContent = promocion.id;
        row.insertCell(1).textContent = promocion.price;
        row.insertCell(2).textContent = promocion.description;
        row.insertCell(3).textContent = promocion.discount;
        row.insertCell(4).textContent = promocion.reason;
        row.insertCell(5).textContent = promocion.state;
        row.insertCell(6).textContent = promocion.cluster;
        row.insertCell(7).textContent = promocion.currency_id;

        const modificarButton = document.createElement('button');
        modificarButton.textContent = 'Modificar';
        modificarButton.className = 'btn btn-success btn-sm modificar-promocion';
        modificarButton.setAttribute('data-id', promocion.id);

        const eliminarButton = document.createElement('button');
        eliminarButton.textContent = 'Eliminar';
        eliminarButton.className = 'btn btn-danger btn-sm eliminar-promocion';
        eliminarButton.setAttribute('data-id', promocion.id);

        const cellAcciones = row.insertCell(8);
        cellAcciones.appendChild(modificarButton);
        cellAcciones.appendChild(eliminarButton);
       // row.cells[0].style.display = 'none';
    });

    setupModificarButtons(promociones);
    setupEliminarButtons();
}

function setupModificarButtons(promociones) {
    document.querySelectorAll('.modificar-promocion').forEach(button => {
        button.addEventListener('click', (event) => {
            const id = event.target.getAttribute('data-id');
            const promocion = promociones.find(promo => promo.id == id);
            if (promocion) { 
                
                document.getElementById('promotionId').value = promocion.id; 
                document.getElementById('promotionPrice').value = promocion.price;
                document.getElementById('promotionDescription').value = promocion.description;
                document.getElementById('promotionDiscount').value = promocion.discount;
                document.getElementById('promotionReason').value = promocion.reason;
                document.getElementById('promotionStatus').value = promocion.state;
                document.getElementById('promotionCurrency').value = promocion.currency_id;
                document.getElementById('promotionCluster').value = promocion.cluster;

                const modal = new bootstrap.Modal(document.getElementById('modalModificaPromocion'));
                modal.show();
            }
        });
    });
}

function setupEliminarButtons() {
    document.querySelectorAll('.eliminar-promocion').forEach(button => {
        button.addEventListener('click', (event) => {
            const id = event.target.getAttribute('data-id');
            const data = { id: id };

            fetch('/productosComerciales_promociones_elimina_promociones', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error('Error:', data.error);
                } else {
                    updateTablePromociones(data.promociones);
                    alert('Promoción eliminada con éxito.');
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
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
             
            }
        })
        .catch(error => {
            console.error('Error:', error);
           
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
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
});