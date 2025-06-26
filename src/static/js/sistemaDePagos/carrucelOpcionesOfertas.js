<<<<<<< HEAD
function handleFormSubmit(event) {
    event.preventDefault();
    cargarOfertaTable();
}

function cargarOfertaTable() {
    const data = {
        account: localStorage.getItem('cuenta'),
        access_token: localStorage.getItem('access_token')
    };

    fetch('/sistemaDePagos_getOfertas/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert('Plan de preaprobación creado con éxito. ID: ' + data.id);
        updateOfertaTable(data.ofertas); // Actualizar la tabla con los nuevos datos
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al crear la suscripción');
    });
}

function updateOfertaTable(ofertas) {
    // Logic to update the offer table with new data
=======
function handleFormSubmit(event) {
    event.preventDefault();
    cargarOfertaTable();
}

function cargarOfertaTable() {
    const data = {
        account: localStorage.getItem('cuenta'),
        access_token: localStorage.getItem('access_token')
    };

    fetch('/sistemaDePagos_getOfertas/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        alert('Plan de preaprobación creado con éxito. ID: ' + data.id);
        updateOfertaTable(data.ofertas); // Actualizar la tabla con los nuevos datos
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al crear la suscripción');
    });
}

function updateOfertaTable(ofertas) {
    // Logic to update the offer table with new data
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
}