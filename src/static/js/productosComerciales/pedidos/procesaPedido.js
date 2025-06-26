<<<<<<< HEAD
$(document).ready(function() {
    $(document).on('submit', '.formClientePedidoJs', function(event) {
        event.preventDefault(); // Prevenir el envío estándar del formulario

        // Obtener el access token almacenado en localStorage
        var access_token_btn_pocesarPedido = localStorage.getItem('access_token');
       
        // Obtener datos del formulario
        var nombreCliente = $('#nombreCliente').val();
        var apellidoCliente = $('#apellidoCliente').val();
        var direccionCliente = $('#direccionCliente').val();
        var telefonoCliente = $('#telefonoCliente').val();
        var emailCliente = $('#emailCliente').val();
        var comentariosCliente = $('#comentariosCliente').val();
        var ambito_pagoPedido = $('#ambito_pagoPedido').val();
        var costo_base = parseFloat($('#costo_base').val()) || 0;
        var porcentaje_retorno = parseFloat($('#porcentaje_retorno').val()) || 0;
        var pedido_data_json = $('#pedido_data_json_pagoPedido').val();
        var cluster_pedido = $('#cluster_pedido').val();
        // Calcular el precio final
        var final_price = costo_base - (costo_base * porcentaje_retorno / 100);

        // Crear los datos de preferencia
        var preference_data = {
            nombreCliente: nombreCliente,
            apellidoCliente: apellidoCliente,
            direccionCliente: direccionCliente,
            telefonoCliente: telefonoCliente,
            emailCliente: emailCliente,
            comentariosCliente: comentariosCliente,
            ambito_pagoPedido: ambito_pagoPedido,
            costo_base: costo_base,
            porcentaje_retorno: porcentaje_retorno,
            final_price: final_price,
            pedido_data_json: pedido_data_json,
            cluster_pedido: cluster_pedido
        };
        debugger;
        // Enviar los datos mediante AJAX con el access token en la cabecera
        $.ajax({
            url: '/productosComerciales_pedidos_process_order/', // URL del backend
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + access_token_btn_pocesarPedido // Agregar el token en el encabezado
            },
            data: JSON.stringify(preference_data),
            success: function(response) {
                alert('Pedido procesado correctamente');
                // Limpiar los campos del formulario
                document.getElementById("nombreCliente").value = '';
                document.getElementById("apellidoCliente").value = '';
                document.getElementById("direccionCliente").value = '';
                document.getElementById("telefonoCliente").value = '';
                document.getElementById("emailCliente").value = '';
                document.getElementById("comentariosCliente").value = '';
            
                // Redirigir al punto de inicio de la preferencia
               // window.location.href = response.init_point;
            },
            
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar el pedido.');
            }
        });
    });
});

=======
$(document).ready(function() {
    $(document).on('submit', '.formClientePedidoJs', function(event) {
        event.preventDefault(); // Prevenir el envío estándar del formulario

        // Obtener el access token almacenado en localStorage
        var access_token_btn_pocesarPedido = localStorage.getItem('access_token');
       
        // Obtener datos del formulario
        var nombreCliente = $('#nombreCliente').val();
        var apellidoCliente = $('#apellidoCliente').val();
        var direccionCliente = $('#direccionCliente').val();
        var telefonoCliente = $('#telefonoCliente').val();
        var emailCliente = $('#emailCliente').val();
        var comentariosCliente = $('#comentariosCliente').val();
        var ambito_pagoPedido = $('#ambito_pagoPedido').val();
        var costo_base = parseFloat($('#costo_base').val()) || 0;
        var porcentaje_retorno = parseFloat($('#porcentaje_retorno').val()) || 0;
        var pedido_data_json = $('#pedido_data_json_pagoPedido').val();
        var cluster_pedido = $('#cluster_pedido').val();
        // Calcular el precio final
        var final_price = costo_base - (costo_base * porcentaje_retorno / 100);

        // Crear los datos de preferencia
        var preference_data = {
            nombreCliente: nombreCliente,
            apellidoCliente: apellidoCliente,
            direccionCliente: direccionCliente,
            telefonoCliente: telefonoCliente,
            emailCliente: emailCliente,
            comentariosCliente: comentariosCliente,
            ambito_pagoPedido: ambito_pagoPedido,
            costo_base: costo_base,
            porcentaje_retorno: porcentaje_retorno,
            final_price: final_price,
            pedido_data_json: pedido_data_json,
            cluster_pedido: cluster_pedido
        };
        debugger;
        // Enviar los datos mediante AJAX con el access token en la cabecera
        $.ajax({
            url: '/productosComerciales_pedidos_process_order/', // URL del backend
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + access_token_btn_pocesarPedido // Agregar el token en el encabezado
            },
            data: JSON.stringify(preference_data),
            success: function(response) {
                alert('Pedido procesado correctamente');
                // Limpiar los campos del formulario
                document.getElementById("nombreCliente").value = '';
                document.getElementById("apellidoCliente").value = '';
                document.getElementById("direccionCliente").value = '';
                document.getElementById("telefonoCliente").value = '';
                document.getElementById("emailCliente").value = '';
                document.getElementById("comentariosCliente").value = '';
            
                // Redirigir al punto de inicio de la preferencia
               // window.location.href = response.init_point;
            },
            
            error: function(xhr, status, error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar el pedido.');
            }
        });
    });
});

>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
