document.addEventListener("DOMContentLoaded", function() {

    //CARGA VALORES  EN INPUT PARA ENVIAR FORM HACIA CARRITO
     // Obtén valores desde localStorage
     var access_token_btn_carrito = localStorage.getItem('access_token') || '';
     var correo_electronico_btn_carrrito = localStorage.getItem('correo_electronico') || '';
     var ambito_btn_carrrito = localStorage.getItem('dominio') || '';
 
     // Asegúrate de que los elementos del DOM existen antes de asignar valores
     if (document.getElementById("access_token_btn_carrito")) {
         document.getElementById("access_token_btn_carrito").value = access_token_btn_carrito;
     }
     if (document.getElementById("correo_electronico_btn_carrrito")) {
         document.getElementById("correo_electronico_btn_carrrito").value = correo_electronico_btn_carrrito;
     }
     if (document.getElementById("ambito_btn_carrrito")) {
         document.getElementById("ambito_btn_carrrito").value = ambito_btn_carrrito;
     }
















 // Función para actualizar el subtotal y el total
 function updateCartTotal() {
    let total = 0;

    // Recorrer todos los items del carrito
    document.querySelectorAll('.cart-item').forEach(item => {
        const unitPrice = parseFloat(item.dataset.precio); // Obtener el precio unitario
        const quantity = parseInt(item.querySelector('.quantity-input').value); // Obtener la cantidad
        total += unitPrice * quantity; // Sumar al total
    });

    // Actualizar los elementos de subtotal y total
    document.getElementById('subtotal').textContent = total.toFixed(2);
    document.getElementById('total').textContent = total.toFixed(2);
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











    // Handle checkout button click
    checkoutButton.addEventListener("click", function() {
        const quantity = parseInt(quantityInput.value);
        const data = { product: "Notebook Asus", quantity: quantity };

        // Send AJAX request to the server
        fetch("/productosComerciales_pedidos_process_order", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
        })
        .catch(error => {
            console.error("Error:", error);
        });
    });
});
