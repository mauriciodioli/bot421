// script.js
//redirige a los links
let planesGlobal = [];
function redirectBroker() {
    var select = document.getElementById('brokerSelect');
    var selectedValue = select.value;
    if (selectedValue) {
        window.open(selectedValue, '_blank');
    }
}


function updatePlansTable(planes) {
    planesGlobal = planes; // Hacer accesible planes globalmente
    
    // Verificar si existe el elemento con ID plansTable
    const table = document.getElementById('plansTable');
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
        modificarButton.textContent = 'Modificar';
        modificarButton.className = 'btn btn-success btn-sm';
        modificarButton.onclick = () => modificarPlan(plan.id);
        row.insertCell(8).appendChild(modificarButton);

        // Crear botón de eliminar
        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Eliminar';
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.onclick = () => deletePlan(plan.id);
        row.insertCell(9).appendChild(deleteButton);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    fetch('/productosComerciales_planes_muestra_planes/', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.planes) {
            console.log(data);
            planesGlobal = data.planes; // Guardar datos en planesGlobal
            updatePlansTable(planesGlobal);
        } else {
            console.error('Error en la respuesta del servidor:', data);
            print('Error al cargar los planes');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cargar los planes');
    });
});

function modificarPlan(planId) {
    // Buscar el plan por ID en planesGlobal
    const plan = planesGlobal.find(p => p.id === planId);

    if (plan) {
        // Llenar el modal con los datos del plan
        document.getElementById('planId').value = plan.id;
        document.getElementById('planFrequency').value = plan.frequency;
        document.getElementById('planAmount').value = plan.amount;
        document.getElementById('planReason').value = plan.reason;
        document.getElementById('planFrequencyType').value = plan.frequency_type;
        document.getElementById('planCurrencyId').value = plan.currency_id;
        document.getElementById('planRepetitions').value = plan.repetitions;
        document.getElementById('planBillingDay').value = plan.billing_day;

        // Mostrar el modal
        const modificarModal = new bootstrap.Modal(document.getElementById('modificarModal'));
        modificarModal.show();
    } else {
        alert('Error: Plan no encontrado');
    }
}

function submitModificarForm() {
    const planId = document.getElementById('planId').value;
    const updatedPlan = {
        id: planId,
        frequency: document.getElementById('planFrequency').value,
        amount: document.getElementById('planAmount').value,
        reason: document.getElementById('planReason').value,
        frequency_type: document.getElementById('planFrequencyType').value,
        currency_id: document.getElementById('planCurrencyId').value,
        repetitions: document.getElementById('planRepetitions').value,
        billing_day: document.getElementById('planBillingDay').value,
        access_token: localStorage.getItem('access_token')
    };

    fetch(`/updatePlanes_preapproval_plan/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedPlan)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Plan modificado con éxito');

            // Actualizar el plan modificado en planesGlobal
            const index = planesGlobal.findIndex(p => p.id === planId);
            if (index !== -1) {
                planesGlobal[index] = updatedPlan;
            }

            // Ocultar el modal
            const modificarModalElement = document.getElementById('modificarModal');
            const bootstrapModal = bootstrap.Modal.getInstance(modificarModalElement);           
            bootstrapModal.hide();

            // Actualizar la tabla
            updatePlansTable(planesGlobal);
           
        } else {
            alert('Error al modificar el plan: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al modificar el plan');
    });
}


function deletePlan(planId) {
    if (confirm('¿Está seguro de que desea eliminar este plan?, luego deber eliminar el plan desde la cuenta de mercado pago para eliminar efectivamente el plan')) {
        const access_token = localStorage.getItem('access_token'); // Obtener el access_token del localStorage

        if (!access_token) {
            alert('No se encontró un token de acceso válido');
            return;
        }

        console.log(`Fetching URL: /deletePlanes_preapproval_plan/${planId}`); // Log para verificar la URL

        fetch(`/deletePlanes_preapproval_plan/${planId}?access_token=${access_token}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => { throw new Error(text) });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('Plan eliminado con éxito');

                // Remover el plan eliminado de planesGlobal
                planesGlobal = planesGlobal.filter(p => p.id !== planId);

                // Actualizar la tabla
                updatePlansTable(planesGlobal);
            } else {
                alert('Error al eliminar el plan');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al eliminar el plan');
        });
    }
}
