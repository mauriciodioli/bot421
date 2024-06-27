
$(document).ready(function(){
    $('#carrucelPromocionOfertasForm').submit(function(event){
        // Prevent the form from submitting and the page from reloading
        event.preventDefault();

        // Log a message to the console to confirm the function was called
        console.log('cargarOfertaTable called');

        // Call the function to handle the form data
        cargarOfertaTable();
    });
});

function cargarOfertaTable() {
    // Log a message to the console to confirm the function was called
    console.log('cargarOfertaTable called');

    // Create an object containing the data to be sent to the server
    const data = {
        correo_electronico: localStorage.getItem('correo_electronico'),
        reason:  document.getElementById('reason').value,
        access_token: localStorage.getItem('access_token')
    };

    // Send the data to the server using a POST request
    fetch('/sistemaDePagos_carrucelPromocionOfertas_get_promociones', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Log the server's response to the console
        console.log(data);

        // Show an alert with the response data
        alert('Plan de preaprobación creado con éxito. ID: ' + data.id);

        // Update the offer table with the new data
        updateOfertaTable(data.ofertas);
    })
    .catch(error => {
        // Log any errors to the console
        console.error('Error:', error);

        // Show an alert indicating that an error occurred
        alert('Error al crear la suscripción');
    });
}

function updateOfertaTable(ofertas) {
    // Logic to update the offer table with new data
}