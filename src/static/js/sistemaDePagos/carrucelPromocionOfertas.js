
$(document).ready(function(){
    
        // Prevent the form from submitting and the page from reloading
    

        // Log a message to the console to confirm the function was called
        console.log('cargarOfertaTable called');

        // Call the function to handle the form data
        cargarOfertaTable();
    
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

          // Actualizar el carrusel con los datos recibidos
          actualizarCarrusel(data.promociones);
    })
    .catch(error => {
        // Log any errors to the console
        console.error('Error:', error);

        // Show an alert indicating that an error occurred
        alert('Error al crear la suscripción');
    });
}


// Función para actualizar el carrusel con las promociones recibidas
function actualizarCarrusel(promociones) {
    // Obtener el elemento del carrusel
    var carouselInner = document.querySelector('.carousel-inner');
    carouselInner.innerHTML = '';  // Limpiar cualquier contenido anterior del carrusel

    // Iterar sobre las promociones recibidas y agregarlas al carrusel
    promociones.forEach(function(promocion, index) {
        var carouselItem = document.createElement('div');
        carouselItem.classList.add('carousel-item');
        if (index === 0) {
            carouselItem.classList.add('active');
        }

        var img = document.createElement('img');
        img.classList.add('d-block', 'w-100');
        img.src = promocion.image_url;
        img.alt = 'Promoción ' + promocion.id;

        var carouselCaption = document.createElement('div');
        carouselCaption.classList.add('carousel-caption');
        carouselCaption.innerHTML = '<h5>' + promocion.description + '</h5><p>' + promocion.price + '</p>';

        carouselItem.appendChild(img);
        carouselItem.appendChild(carouselCaption);
        carouselInner.appendChild(carouselItem);
    });
}
