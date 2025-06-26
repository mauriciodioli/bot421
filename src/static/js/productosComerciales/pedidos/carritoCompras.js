function goBack() {
    window.history.back();  // Retrocede a la página anterior
}

document.addEventListener("DOMContentLoaded", function() {

    //CARGA VALORES  EN INPUT PARA ENVIAR FORM HACIA CARRITO
     // Obtén valores desde localStorage
     
     var access_token_btn_carrito = localStorage.getItem('access_token') || '';
     var correo_electronico_btn_carrito = localStorage.getItem('correo_electronico') || '';
     var ambito_btn_carrito = localStorage.getItem('dominio') || '';
 
     // Asegúrate de que los elementos del DOM existen antes de asignar valores
     if (document.getElementById("access_token_btn_carrito")) {
         document.getElementById("access_token_btn_carrito").value = access_token_btn_carrito;
     }
     if (document.getElementById("access_token_btn_carrito1")) {
        document.getElementById("access_token_btn_carrito1").value = access_token_btn_carrito;
    }
     if (document.getElementById("correo_electronico_btn_carrito")) {
         document.getElementById("correo_electronico_btn_carrito").value = correo_electronico_btn_carrito;
     }
     if (document.getElementById("ambito_btn_carrito")) {
         document.getElementById("ambito_btn_carrito").value = ambito_btn_carrito;
     }










    






 // Función para actualizar el subtotal y el total

 function updateCartTotal() {
    let total = 0;

    // Recorrer todos los items del carrito
    document.querySelectorAll('.cart-item').forEach(item => {
        const unitPrice = parseFloat(item.dataset.precio) || 0; // Manejar casos donde no hay precio
        const quantity = parseInt(item.querySelector('.quantity-input')?.value) || 0; // Manejar casos donde no hay cantidad
        total += unitPrice * quantity; // Sumar al total
    });

    // Actualizar los elementos de subtotal y total solo si existen
    const subtotalElement = document.getElementById('subtotal');
    const totalElement = document.getElementById('total');

    if (subtotalElement) {
        subtotalElement.textContent = total.toFixed(2);
    }
    if (totalElement) {
        totalElement.textContent = total.toFixed(2);
    }
}


// Detectar cambios en las cantidades
document.querySelectorAll('.quantity-input').forEach(input => {
    input.addEventListener('input', () => {
        updateCartTotal(); // Recalcular el total cuando cambie la cantidad
    });
});

// Calcular el total inicial
updateCartTotal();

















//////////////////////////////////////////////////////////////////////
///////////////////////eliminar pedido///////////////////////////////
//////////////////////////////////////////////////////////////////////
const removeButtons = document.querySelectorAll('.remove-button');

// Función para recalcular el subtotal y total
function recalculateTotal() {
    try {
        let subtotal = 0;

        // Verificar si los elementos subtotal y total están presentes
        const subtotalElement = document.getElementById('subtotal');
        const totalElement = document.getElementById('total');

        if (!subtotalElement || !totalElement) {
            console.warn('Los elementos "subtotal" o "total" no están presentes en el DOM. No se realizará ninguna actualización.');
            return;
        }

        // Verificar si hay elementos con la clase 'cart-item'
        const cartItems = document.querySelectorAll('.cart-item');
        if (cartItems.length === 0) {
            console.warn('No se encontraron elementos en el carrito.');
            return;
        }

        // Iterar sobre todos los elementos visibles en el carrito
        cartItems.forEach(item => {
            // Manejar posibles excepciones al acceder a atributos y valores
            const precio = parseFloat(item.getAttribute('data-precio')) || 0;
            const cantidadInput = item.querySelector('.quantity-input');
            if (!cantidadInput) {
                console.warn('No se encontró un input de cantidad para un elemento del carrito.');
                return;
            }

            const cantidad = parseInt(cantidadInput.value) || 1;
            subtotal += precio * cantidad;
        });

        // Actualizar los valores en el DOM solo si los elementos están presentes
        subtotalElement.textContent = subtotal.toFixed(2);
        totalElement.textContent = subtotal.toFixed(2);

    } catch (error) {
        console.error('Ocurrió un error al recalcular el total:', error);
    }
}




// Listener para eliminar elementos
removeButtons.forEach(button => {
    button.addEventListener('click', function () {
        const pedidoId = this.getAttribute('data-pedido-id');
        
        fetch('/productosComerciales_pedidos_eliminar_carrito/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ pedido_id: pedidoId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Eliminar el elemento del DOM
                this.closest('.cart-item').remove();

                // Recalcular el subtotal y total
                recalculateTotal();
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error al eliminar el pedido:', error);
            alert('Hubo un error al procesar la solicitud.');
        });
    });
});

// Calcular el total inicial al cargar la página
recalculateTotal();











});
