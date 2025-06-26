<<<<<<< HEAD
// Obtener el ID del usuario del localStorage
const localUserId = localStorage.getItem('usuario_id');

// Mostrar u ocultar botones "Eliminar" según el user_id
document.querySelectorAll('.remove-button').forEach(button => {
    const consultaUserId = button.getAttribute('data-user-id');
    
    if (localUserId === consultaUserId) {
        button.style.display = 'inline-block'; // Mostrar botón
    }
});









// Obtener el modal
var modal = document.getElementById("detalleModal");

// Obtener el botón de cerrar
var span = document.getElementsByClassName("close")[0];

// Función para abrir el modal con los datos de la publicación
function mostrarDetalle(consultaId) {
    // Llamada AJAX para obtener los datos de la publicación
    fetch(`/obtener_detalle_publicacion/${consultaId}`)
        .then(response => response.json())
        .then(data => {
            // Rellenar el modal con los datos de la publicación
            document.getElementById('productoNombre').textContent = data.nombre_producto;
            document.getElementById('productoDescripcion').textContent = data.descripcion;
            document.getElementById('productoTexto').textContent = data.texto;
            document.getElementById('productoCorreo').textContent = data.correoElectronico;
            document.getElementById('productoFecha').textContent = data.fechaCreacion;
            document.getElementById('productoUserId').textContent = data.user_id;
            
            // Mostrar el modal
            modal.style.display = "block";
        })
        .catch(error => console.log("Error al obtener los datos:", error));
}

// Agregar el evento de clic para cada botón de "Detalle"
document.querySelectorAll('.detalleProducto').forEach(button => {
    button.addEventListener('click', function () {
        var consultaId = this.getAttribute('data-consulta-id');
        mostrarDetalle(consultaId);  // Llamada a la nueva función
    });
});

// Cuando el usuario hace clic en el botón de cerrar, cierra el modal
span.onclick = function () {
    modal.style.display = "none";
}

// Cuando el usuario hace clic fuera del modal, cierra el modal
window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}
















$(document).ready(function() {
    // Función para realizar la búsqueda
    function realizarBusqueda() {
        var consulta = $('#consulta_publicaciones_data').val();
        var ambito = localStorage.getItem('dominio');
        var accessToken = localStorage.getItem('access_token');
        
        // Verifica si hay texto en el campo
        if (consulta.trim() !== "") {
            $.ajax({
                url: '/media_consultaPublicaciones_lupa_muestra/',  // URL de la ruta
                type: 'POST',
                data: {
                    consulta: consulta,  // Envía el texto de búsqueda al servidor
                    ambito: ambito,
                    accessToken: accessToken
                },
                success: function(response) {
                    // Verifica si hay datos en la respuesta
                    if (response.data && response.data.length > 0) {
                        var tableContent = '';
                        var total = 0;
                        var subtotal = 0;
                        
                        // Recorre los datos y construye el HTML de la tabla
                        response.data.forEach(function(consulta) {
                            subtotal += parseFloat(consulta.precio_venta) || 0;  // Sumar precios al subtotal
                            tableContent += `
                                <tr data-precio="${consulta.precio_venta}" data-id="${consulta.id}">
                                    <td>
                                        ${consulta.imagen_url ? 
                                            `<img src="${consulta.imagen_url}" alt="Imagen del producto" class="product-image">` : 
                                            `<img src="default.jpg" alt="Producto sin imagen" class="product-image">`}
                                    </td>
                                    <td class="text">${consulta.nombre_producto}</td>
                                    <td class="price">
                                        <span class="unit-price">${consulta.precio_venta}</span>
                                    </td>
                                    <td>
                                        <input type="number" id="quantity-${consulta.id}" name="quantity" class="quantity-input" value="1" min="1">
                                    </td>
                                    <td>
                                        <input type="checkbox" class="estado-checkbox" onchange="agregarListado(${consulta.id}, this)" 
                                               ${consulta.precio_venta === 'entregado' ? 'checked' : ''}>
                                    </td>
                                    <td>
                                        <button class="remove-button" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}" style="display: none;">
                                            Eliminar
                                        </button>
                                    </td>
                                    <td>
                                        <button class="btn-success detalleProducto" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}">
                                            Detalle
                                        </button>
                                    </td>
                                </tr>
                            `;
                        });
                        
                        // Calcular el total (esto depende de tu lógica)
                        total = subtotal;  // O ajusta según sea necesario
    
                        // Inserta el contenido generado en el contenedor de la tabla
                        $('.table-container tbody').html(tableContent);
                        
                        // Mostrar el resumen del carrito
                        var cartSummary = `...`; // El resumen del carrito sigue igual
                        $('.cart-summary-container').html(cartSummary);
                        
                        // Asignar el evento click a los botones "Detalle" después de que el contenido haya sido insertado
                        $('.detalleProducto').click(function() {
                            var consultaId = $(this).data('consulta-id');
                            var userId = $(this).data('user-id');
                            
                            // Llamar a la función para mostrar el modal
                            mostrarDetalle(consultaId, userId); 
                                                });
                        

                    } else {
                        console.log("No se encontraron publicaciones.");
                        $('.table-container tbody').html('<tr><td colspan="7">No se encontraron publicaciones.</td></tr>');
                        $('.cart-summary-container').html('');  // Ocultar el resumen si no hay datos
                    }
                },
                error: function(xhr, status, error) {
                    console.log('Error al realizar la búsqueda:', error);
                }
            });
        } else {
            console.log("Por favor ingrese una consulta.");
        }
    }
    
    // Llamar a la función cuando se hace clic en el ícono de lupa
    $('#search_button').click(function() {
        realizarBusqueda();
    });

    // También permitir la búsqueda presionando Enter
    $('#consulta_publicaciones_data').keypress(function(e) {
        if (e.which == 13) { // 13 es el código de la tecla Enter
            realizarBusqueda();
        }
    });
});
















function agregarListado(pedidoId, checkbox) { 
    debugger;
    if (!checkbox.checked) {
        console.log(`El pedido con ID ${pedidoId} no se enviará porque el checkbox no está marcado.`);
        return; // Salir de la función si el checkbox no está marcado
    }
    const nuevoEstado = checkbox.checked ? 'activo' : 'inactivo';  // Determinar el nuevo estado
    const access_token_btn_carrito1 = localStorage.getItem('access_token');
    const correo_electronico_cbox = localStorage.getItem('correo_electronico');
    const ambito_btn_carrito = localStorage.getItem('dominio');
    
    // Obtén el campo de cantidad usando el pedidoId
    const quantityInput = document.querySelector(`#quantity-${pedidoId}`);
    const cantidadSeleccionada = quantityInput ? quantityInput.value : null;

    console.log(`Pedido ID: ${pedidoId}, Nuevo Estado: ${nuevoEstado}, Cantidad: ${cantidadSeleccionada}`);
    
    
    fetch(`/productosComerciales_pedidos_alta_carrito_checkBox/${pedidoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ estado: nuevoEstado,
            access_token_btn_carrito1: access_token_btn_carrito1,
            correo_electronico_cbox: correo_electronico_cbox,
            ambito_btn_carrito: ambito_btn_carrito,
            publicacion_id: pedidoId,
            cantidadCompra: cantidadSeleccionada, // Incluye la cantidad
            checkbox: checkbox.checked            
         })  // Enviar el estado en el cuerpo
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Agregado al carrito correctamente'); // Muestra el mensaje de éxito
        } else {
            alert(data.message || 'No se pudo actualizar el carrito'); // Muestra mensaje del servidor
        }
    })
    .catch(error => {
        console.error('Error al actualizar el carrito:', error);
        alert('Hubo un error al actualizar el carrito');
    });
}





document.querySelector('.card-button').addEventListener('click', function () {
    const selectedProducts = Array.from(document.querySelectorAll('.estado-checkbox:checked')).map(checkbox => {
        const row = checkbox.closest('tr');
        return {
            id: row.dataset.id,
            nombre_producto: row.querySelector('.text').textContent.trim(),
            precio_venta: row.querySelector('.unit-price').textContent.trim(),
            cantidad: row.querySelector('.quantity-input').value
        };
    });

    // Convertir los datos seleccionados en JSON y asignarlos al campo oculto
    document.getElementById('consulta_data').value = JSON.stringify(selectedProducts);

    // Opcionalmente, puedes actualizar el total
    const total = selectedProducts.reduce((sum, product) => sum + (parseFloat(product.precio_venta) * parseInt(product.cantidad, 10)), 0);
    document.getElementById('total_pago').value = total.toFixed(2);
});
=======
// Obtener el ID del usuario del localStorage
const localUserId = localStorage.getItem('usuario_id');

// Mostrar u ocultar botones "Eliminar" según el user_id
document.querySelectorAll('.remove-button').forEach(button => {
    const consultaUserId = button.getAttribute('data-user-id');
    
    if (localUserId === consultaUserId) {
        button.style.display = 'inline-block'; // Mostrar botón
    }
});









// Obtener el modal
var modal = document.getElementById("detalleModal");

// Obtener el botón de cerrar
var span = document.getElementsByClassName("close")[0];

// Función para abrir el modal con los datos de la publicación
function mostrarDetalle(consultaId) {
    // Llamada AJAX para obtener los datos de la publicación
    fetch(`/obtener_detalle_publicacion/${consultaId}`)
        .then(response => response.json())
        .then(data => {
            // Rellenar el modal con los datos de la publicación
            document.getElementById('productoNombre').textContent = data.nombre_producto;
            document.getElementById('productoDescripcion').textContent = data.descripcion;
            document.getElementById('productoTexto').textContent = data.texto;
            document.getElementById('productoCorreo').textContent = data.correoElectronico;
            document.getElementById('productoFecha').textContent = data.fechaCreacion;
            document.getElementById('productoUserId').textContent = data.user_id;
            
            // Mostrar el modal
            modal.style.display = "block";
        })
        .catch(error => console.log("Error al obtener los datos:", error));
}

// Agregar el evento de clic para cada botón de "Detalle"
document.querySelectorAll('.detalleProducto').forEach(button => {
    button.addEventListener('click', function () {
        var consultaId = this.getAttribute('data-consulta-id');
        mostrarDetalle(consultaId);  // Llamada a la nueva función
    });
});

// Cuando el usuario hace clic en el botón de cerrar, cierra el modal
span.onclick = function () {
    modal.style.display = "none";
}

// Cuando el usuario hace clic fuera del modal, cierra el modal
window.onclick = function (event) {
    if (event.target === modal) {
        modal.style.display = "none";
    }
}
















$(document).ready(function() {
    // Función para realizar la búsqueda
    function realizarBusqueda() {
        var consulta = $('#consulta_publicaciones_data').val();
        var ambito = localStorage.getItem('dominio');
        var accessToken = localStorage.getItem('access_token');
        
        // Verifica si hay texto en el campo
        if (consulta.trim() !== "") {
            $.ajax({
                url: '/media_consultaPublicaciones_lupa_muestra/',  // URL de la ruta
                type: 'POST',
                data: {
                    consulta: consulta,  // Envía el texto de búsqueda al servidor
                    ambito: ambito,
                    accessToken: accessToken
                },
                success: function(response) {
                    // Verifica si hay datos en la respuesta
                    if (response.data && response.data.length > 0) {
                        var tableContent = '';
                        var total = 0;
                        var subtotal = 0;
                        
                        // Recorre los datos y construye el HTML de la tabla
                        response.data.forEach(function(consulta) {
                            subtotal += parseFloat(consulta.precio_venta) || 0;  // Sumar precios al subtotal
                            tableContent += `
                                <tr data-precio="${consulta.precio_venta}" data-id="${consulta.id}">
                                    <td>
                                        ${consulta.imagen_url ? 
                                            `<img src="${consulta.imagen_url}" alt="Imagen del producto" class="product-image">` : 
                                            `<img src="default.jpg" alt="Producto sin imagen" class="product-image">`}
                                    </td>
                                    <td class="text">${consulta.nombre_producto}</td>
                                    <td class="price">
                                        <span class="unit-price">${consulta.precio_venta}</span>
                                    </td>
                                    <td>
                                        <input type="number" id="quantity-${consulta.id}" name="quantity" class="quantity-input" value="1" min="1">
                                    </td>
                                    <td>
                                        <input type="checkbox" class="estado-checkbox" onchange="agregarListado(${consulta.id}, this)" 
                                               ${consulta.precio_venta === 'entregado' ? 'checked' : ''}>
                                    </td>
                                    <td>
                                        <button class="remove-button" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}" style="display: none;">
                                            Eliminar
                                        </button>
                                    </td>
                                    <td>
                                        <button class="btn-success detalleProducto" data-consulta-id="${consulta.id}" data-user-id="${consulta.user_id}">
                                            Detalle
                                        </button>
                                    </td>
                                </tr>
                            `;
                        });
                        
                        // Calcular el total (esto depende de tu lógica)
                        total = subtotal;  // O ajusta según sea necesario
    
                        // Inserta el contenido generado en el contenedor de la tabla
                        $('.table-container tbody').html(tableContent);
                        
                        // Mostrar el resumen del carrito
                        var cartSummary = `...`; // El resumen del carrito sigue igual
                        $('.cart-summary-container').html(cartSummary);
                        
                        // Asignar el evento click a los botones "Detalle" después de que el contenido haya sido insertado
                        $('.detalleProducto').click(function() {
                            var consultaId = $(this).data('consulta-id');
                            var userId = $(this).data('user-id');
                            
                            // Llamar a la función para mostrar el modal
                            mostrarDetalle(consultaId, userId); 
                                                });
                        

                    } else {
                        console.log("No se encontraron publicaciones.");
                        $('.table-container tbody').html('<tr><td colspan="7">No se encontraron publicaciones.</td></tr>');
                        $('.cart-summary-container').html('');  // Ocultar el resumen si no hay datos
                    }
                },
                error: function(xhr, status, error) {
                    console.log('Error al realizar la búsqueda:', error);
                }
            });
        } else {
            console.log("Por favor ingrese una consulta.");
        }
    }
    
    // Llamar a la función cuando se hace clic en el ícono de lupa
    $('#search_button').click(function() {
        realizarBusqueda();
    });

    // También permitir la búsqueda presionando Enter
    $('#consulta_publicaciones_data').keypress(function(e) {
        if (e.which == 13) { // 13 es el código de la tecla Enter
            realizarBusqueda();
        }
    });
});
















function agregarListado(pedidoId, checkbox) { 
    debugger;
    if (!checkbox.checked) {
        console.log(`El pedido con ID ${pedidoId} no se enviará porque el checkbox no está marcado.`);
        return; // Salir de la función si el checkbox no está marcado
    }
    const nuevoEstado = checkbox.checked ? 'activo' : 'inactivo';  // Determinar el nuevo estado
    const access_token_btn_carrito1 = localStorage.getItem('access_token');
    const correo_electronico_cbox = localStorage.getItem('correo_electronico');
    const ambito_btn_carrito = localStorage.getItem('dominio');
    
    // Obtén el campo de cantidad usando el pedidoId
    const quantityInput = document.querySelector(`#quantity-${pedidoId}`);
    const cantidadSeleccionada = quantityInput ? quantityInput.value : null;

    console.log(`Pedido ID: ${pedidoId}, Nuevo Estado: ${nuevoEstado}, Cantidad: ${cantidadSeleccionada}`);
    
    
    fetch(`/productosComerciales_pedidos_alta_carrito_checkBox/${pedidoId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ estado: nuevoEstado,
            access_token_btn_carrito1: access_token_btn_carrito1,
            correo_electronico_cbox: correo_electronico_cbox,
            ambito_btn_carrito: ambito_btn_carrito,
            publicacion_id: pedidoId,
            cantidadCompra: cantidadSeleccionada, // Incluye la cantidad
            checkbox: checkbox.checked            
         })  // Enviar el estado en el cuerpo
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Agregado al carrito correctamente'); // Muestra el mensaje de éxito
        } else {
            alert(data.message || 'No se pudo actualizar el carrito'); // Muestra mensaje del servidor
        }
    })
    .catch(error => {
        console.error('Error al actualizar el carrito:', error);
        alert('Hubo un error al actualizar el carrito');
    });
}





document.querySelector('.card-button').addEventListener('click', function () {
    const selectedProducts = Array.from(document.querySelectorAll('.estado-checkbox:checked')).map(checkbox => {
        const row = checkbox.closest('tr');
        return {
            id: row.dataset.id,
            nombre_producto: row.querySelector('.text').textContent.trim(),
            precio_venta: row.querySelector('.unit-price').textContent.trim(),
            cantidad: row.querySelector('.quantity-input').value
        };
    });

    // Convertir los datos seleccionados en JSON y asignarlos al campo oculto
    document.getElementById('consulta_data').value = JSON.stringify(selectedProducts);

    // Opcionalmente, puedes actualizar el total
    const total = selectedProducts.reduce((sum, product) => sum + (parseFloat(product.precio_venta) * parseInt(product.cantidad, 10)), 0);
    document.getElementById('total_pago').value = total.toFixed(2);
});
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
