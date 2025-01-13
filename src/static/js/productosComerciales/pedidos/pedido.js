 //alamcen datos para enviar al boton donacion 
 var access_token_btn_finalizarPago = localStorage.getItem('access_token');
 var correo_electronico_btn_finalizarPago = localStorage.getItem('correo_electronico');
 document.getElementById('access_token_btn_finalizarPago').value = access_token_btn_finalizarPago;
 document.getElementById('correo_electronico_btn_finalizarPago').value = correo_electronico_btn_finalizarPago;






























document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('.custom-dropdown-menu').addEventListener('click', function(e) {
        if (e.target && e.target.matches('.dropdown-item')) {
            const itemValue = e.target.id;  // Usamos el ID del enlace
            console.log('Valor del id:', itemValue);
            muestraCarritoPorDominio(itemValue);
        }
    });
});

function muestraCarritoPorDominio(itemValue) {
    var access_token = localStorage.getItem('access_token');
    var formData = { ambito_carrito: itemValue, access_token: access_token };

    fetch('/productosComerciales_pedidos_mostrar_layout_carrito/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        const carritoContainer = document.querySelector('.cart-container');

        // Limpiar el contenido anterior del contenedor
        carritoContainer.innerHTML = `<h3 style="color:black;">Carrito de Compras en:  ${itemValue}</h3>`;

        // Verificar si hay productos en el carrito
        if (data.pedidos_data && data.pedidos_data.length > 0) {
            // Agregar los productos al carrito
            data.pedidos_data.forEach(pedido => {
                const cartItem = document.createElement('div');
                cartItem.classList.add('cart-item');
                cartItem.setAttribute('data-precio', pedido.precio_venta);
                cartItem.setAttribute('data-id', pedido.id);

                cartItem.innerHTML = `
                    ${pedido.imagen_url ? 
                        `<img src="${pedido.imagen_url}" alt="Imagen del producto" class="product-image">` : 
                        `<img src="default.jpg" alt="Producto sin imagen" class="product-image">`}
                    <div class="product-details">
                        <h2>${pedido.nombre_producto}</h2>
                        <p class="price">Precio: $<span class="unit-price">${pedido.precio_venta}</span></p>
                        <label for="quantity-${pedido.id}">Cantidad:</label>
                        <input type="number" id="quantity-${pedido.id}" name="quantity" class="quantity-input" value="1" min="1">
                        <button class="remove-button" data-pedido-id="${pedido.id}">Eliminar</button>
                    </div>
                `;
                carritoContainer.appendChild(cartItem);
            });

            // Crear y agregar el resumen del carrito
            const cartSummary = document.createElement('div');
            cartSummary.classList.add('cart-summary');
            cartSummary.innerHTML = `
                <p>Subtotal: $<span id="subtotal">0.00</span></p>
                <p>Total: $<span id="total">0.00</span></p>
                <button id="return-button" style="margin-right: 200px;" onclick="goBack()">Volver</button>
                <button id="checkout-button">Finalizar la compra</button>
            `;
            carritoContainer.appendChild(cartSummary);

            // Llamar para recalcular el total después de cargar el carrito
            recalculateTotal();
        } else {
              // Mostrar mensaje si no hay productos en el carrito, incluyendo el ambito
              carritoContainer.innerHTML = `<h3 style="color:black;">No tienes productos en el carrito para el ámbito: ${itemValue}.</h3>`;
        }
    })
    .catch(error => {
        console.error('Error al cargar el carrito:', error);
    });
}


// Delegación de eventos para los botones de eliminar
document.querySelector('.cart-container').addEventListener('click', function(e) {
    // Eliminar producto
    if (e.target && e.target.matches('.remove-button')) {
        const pedidoId = e.target.getAttribute('data-pedido-id');

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
                e.target.closest('.cart-item').remove();

                // Recalcular el subtotal y total después de eliminar
                recalculateTotal();
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error('Error al eliminar el pedido:', error);
            alert('Hubo un error al procesar la solicitud.');
        });
    }
});

// Función para recalcular el subtotal y total
function recalculateTotal() {
    let subtotal = 0;

    // Iterar sobre todos los elementos visibles en el carrito
    document.querySelectorAll('.cart-item').forEach(item => {
        const precio = parseFloat(item.getAttribute('data-precio')) || 0;
        const cantidad = parseInt(item.querySelector('.quantity-input').value) || 1;

        subtotal += precio * cantidad;
    });

    // Actualizar el subtotal y total en el DOM
    document.getElementById('subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('total').textContent = subtotal.toFixed(2); // Si tienes impuestos o descuentos, aplica aquí
    // Llamar a la función para actualizar el valor del total en el formulario
    document.getElementById('total_pago').value = subtotal.toFixed(2);
   
}

// Listener para los cambios de cantidad
document.querySelector('.cart-container').addEventListener('input', function(e) {
    if (e.target && e.target.matches('.quantity-input')) {
        // Recalcular el total cuando se cambie la cantidad
        recalculateTotal();
    }
});

// Calcular el total inicial cuando la página carga
recalculateTotal();
