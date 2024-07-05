
$(document).ready(function(){
    
        // Prevent the form from submitting and the page from reloading
    

        // Log a message to the console to confirm the function was called
        console.log('cargarOfertaTable called');

        // Call the function to handle the form data
       // cargarOfertaTable();
    
});

function cargarOfertaTable() {
    // Log a message to the console to confirm the function was called
    console.log('cargarOfertaTable called');
    if (document.getElementById('reason')) {
        reason = document.getElementById('reason').value;
    } else {
        reason = 'no tiene';
    }

    const data = {        
        reason: reason,
        correo_electronico: localStorage.getItem('correo_electronico'),
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







$(document).ready(function(){
    $(document).on('submit', '.donationForm', function(event){
        event.preventDefault(); // Evita que el formulario se envíe de manera convencional
        
        // Obtén los datos del formulario
        var formData = {
            costo_base: $(this).find('input[name="costo_base"]').val(),
            porcentaje_retorno: $(this).find('input[name="porcentaje_retorno"]').val()
        };
  
        // Crea los datos de la preferencia
        var preference_data = {
            items: [
                {
                    title: "Donacion de prueba",
                    quantity: 1,
                    unit_price: parseFloat(formData.costo_base) // Asegúrate de convertir a número
                }
            ],
            back_urls: {
                success: "https://89ae-190-225-182-66.ngrok-free.app/success",
                failure: "https://89ae-190-225-182-66.ngrok-free.app/failure",
                pending: "https://89ae-190-225-182-66.ngrok-free.app/pending"
            },
            notification_url: "https://89ae-190-225-182-66.ngrok-free.app/webhook",
            auto_return: "approved"
        };
  
        // Envía la solicitud AJAX
        $.ajax({
            url: '/create_order/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(preference_data),
            success: function(response) {
                // Redirige a la URL de inicialización de la preferencia
                window.location.href = response.init_point;
            },
            error: function(xhr, status, error) {
                console.error('Error: ' + error);
                alert('Hubo un error al procesar la donación.');
            }
        });
    });
});
