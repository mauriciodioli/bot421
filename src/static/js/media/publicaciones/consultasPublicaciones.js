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
                url: '/media_consultaPublicaciones_lupa_muestra',  // URL de la ruta
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
                        // Mostrar el resumen del carrito
                        var cartSummary = `
                            <div class="cart-summary">
                                <div class="summary-details">
                                    <p>Subtotal: $<span id="subtotal">${subtotal.toFixed(2)}</span></p>
                                    <p>Total: $<span id="total">${total.toFixed(2)}</span></p>
                                </div>

                                <div class="buttons-container">
                                    <button id="return-button" onclick="goBack()">Volver</button>

                                    <form id="sistemaDePagos_pagoconsultas" method="POST" action="/sistemaDePagos_pagoconsultas/">
                                        <input type="hidden" id="access_token_btn_finalizarPago" name="access_token_btn_finalizarPago">
                                        <input type="hidden" id="correo_electronico_btn_finalizarPago" name="correo_electronico_btn_finalizarPago"> 
                                        <input type="hidden" id="productoComercial" name="productoComercial" value='finalizarPago'> 
                                        <input type="hidden" id="cluster_btn_finalizarPago" name="cluster_btn_finalizarPago" value='1'>        
                                        <input type="hidden" id="ambito_btn_finalizarPago" name="ambito_btn_finalizarPago"> 
                                        <input type="hidden" id="layoutOrigen" name="layoutOrigen" value="layout">
                                        <input type="hidden" id="consulta_data" name="consulta_data">

                                        <!-- Campo oculto para enviar el total -->
                                        <input type="hidden" id="total_pago" name="total_pago" value="${total.toFixed(2)}">
                                    
                                        <button class="card-button btn-success long-button" type="submit" style="color: green;">Elegir pago</button>
                                    </form>
                                </div>
                            </div>
                        `;

                        $('.cart-summary-container').html(cartSummary);

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
