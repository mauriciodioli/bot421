document.addEventListener('DOMContentLoaded', function () {

    document.querySelector('.custom-dropdown-menu').addEventListener('click', function(e) {
        if (e.target && e.target.matches('.dropdown-item')) {
            // Mostrar el objeto del elemento clickeado en la consola
           // console.log('Elemento clickeado:', e.target);
            
            // Obtener el valor del id
            const itemValue = e.target.id;  // Usamos el ID del enlace
            console.log('Valor del id:', itemValue);
            // Lógica de manejo del clic
            // Llamar a la función para cargar el carrito o realizar alguna acción
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
    .then(response => {
        if (!response.ok) {
            throw new Error('Error al cargar el carrito.');
        }
        return response.json();  // Obtener los datos en formato JSON
    })
    .then(data => {
        const carritoContainer = document.querySelector('.cart-container');

        // Limpiar el contenido anterior del contenedor
        carritoContainer.innerHTML = `
            <h1>Carrito de Compras</h1>
        `;

        // Agregar los productos del carrito
        data.pedidos_data.forEach(pedido => {
            const cartItem = document.createElement('div');
            cartItem.classList.add('cart-item');
            cartItem.setAttribute('data-precio', pedido.precio_venta);
            cartItem.setAttribute('data-id', pedido.id);

            cartItem.innerHTML = `
                ${pedido.imagen_url ? `<img src="${pedido.imagen_url}" alt="Imagen del producto" class="product-image">` : 
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

        // Actualizar el subtotal y el total
        let subtotal = 0;
        data.pedidos_data.forEach(pedido => {
            subtotal += pedido.precio_venta;
        });

        // Crear y añadir la sección de resumen del carrito con los botones
        const cartSummary = document.createElement('div');
        cartSummary.classList.add('cart-summary');
        cartSummary.innerHTML = `
            <p>Subtotal: $<span id="subtotal">${subtotal.toFixed(2)}</span></p>
            <p>Total: $<span id="total">${subtotal.toFixed(2)}</span></p>
            <button id="return-button" style="margin-right: 200px;" onclick="goBack()">Volver</button>
            <button id="checkout-button">Finalizar la compra</button>
        `;
        carritoContainer.appendChild(cartSummary);
    })
    .catch(error => {
        console.error('Error al enviar datos:', error);
    });
}













//////////////////////////////////////////////////////////////////////
///////////////////////eliminar pedido///////////////////////////////
//////////////////////////////////////////////////////////////////////
const removeButtons = document.querySelectorAll('.remove-button');

// Función para recalcular el subtotal y total
function recalculateTotal() {
    let subtotal = 0;

    // Iterar sobre todos los elementos visibles en el carrito
    document.querySelectorAll('.cart-item').forEach(item => {
        const precio = parseFloat(item.getAttribute('data-precio')) || 0;
        const cantidad = parseInt(item.querySelector('.quantity-input').value) || 1;

        subtotal += precio * cantidad;
    });

    // Actualizar los valores en el DOM
    document.getElementById('subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('total').textContent = subtotal.toFixed(2); // Si tienes impuestos o descuentos, aplica aquí
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