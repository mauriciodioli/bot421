document.addEventListener('DOMContentLoaded', function () {
    const accessToken = localStorage.getItem('access_token');
    const ambito_pagoPedido = localStorage.getItem('dominio');
    if (accessToken) {
        document.getElementById('accessToken_pagoPedido').value = accessToken;
        document.getElementById('ambito_pagoPedido').value = ambito_pagoPedido;
    } else {
        console.warn('Access token no encontrado en localStorage');
    }
});





$(document).ready(function () {
    $(document).on('submit', '.pagoPedidoForm', function (event) {
        event.preventDefault();
        // Obtener el access token almacenado en localStorage
        var accessToken_pagoPedido = localStorage.getItem('access_token');


        // Obtener datos del formulario
        var costo_base = parseFloat($(this).find('input[name="costo_base"]').val()) || 0;
        var porcentaje_retorno = parseFloat($(this).find('input[name="discount"]').val()) || 0;
        var titulo = $(this).find('input[name="reason"]').val() || '';
        var currency_id = $(this).find('input[name="currency_id"]').val() || 'USD';

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
            title: titulo,
            porcentaje_retorno: porcentaje_retorno,
            quantity: 1,
            currency_id: currency_id,
            unit_price: costo_base,
            final_price: final_price,
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

        // Enviar datos mediante AJAX
        $.ajax({
            url: '/sistemaDePagos_create_order/',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + accessToken_pagoPedido // Agregar el token en el encabezado
            },
            data: JSON.stringify(preference_data),
            success: function (response) {
                if (response.init_point) {
                    window.location.href = response.init_point;
                }
            },
            error: function (xhr, status, error) {
                console.error('Error:', error);
                alert('Hubo un error al procesar el pedido.');
            },
        });
    });
});


























function createOrderPaypal() {
    const form = document.querySelector('.pagoPedidoForm');
    const formData = new FormData(form);
  
    const formObj = {};
    formData.forEach((value, key) => {
        formObj[key] = value;
    });

    return fetch('/create_orders_paypal/', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formObj)
    })
    .then(res => res.json())
    .then(data => {
        console.log("Orden PayPal creada:", data.orderID);
        return data.orderID;
    })
    .catch(err => {
        console.error("Error al crear orden PayPal:", err);
        alert("No se pudo crear la orden de PayPal.");
        throw err;
    });
}





function capturarOrdenPaypal(orderID) {
    const form = document.querySelector('.pagoPedidoForm');
    const formData = new FormData(form);

    const formObj = {};
    formData.forEach((value, key) => {
        formObj[key] = value;
    });

    // fetch con el orderID en la URL (correcto)
    return fetch(`/capture_order_paypal/${orderID}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formObj)
    })
    .then(res => res.json())
    .then(response => {
        console.log("Respuesta del backend:", response);
        alert("Pago confirmado con PayPal.");
        return response;
    })
    .catch(err => {
        console.error("Error al capturar:", err);
        alert("Error al confirmar pago con PayPal.");
        throw err;
    });
}



function abrirModalPago() {
  document.getElementById("modalPagoPaypal").style.display = "block";

  if (document.getElementById("paypal-button-container").childElementCount === 0) {
    createOrderPaypal().then(orderID => {
      paypal.Buttons({
        createOrder: () => orderID,
        onApprove: (data, actions) => {
          capturarOrdenPaypal(data.orderID);
        }
      }).render('#paypal-button-container');
    });
  }
}



function abrirModalPago() {
  const modal = document.getElementById("modalPagoPaypal");
  modal.classList.add("activo");

  const container = document.getElementById("paypal-button-container");
  container.innerHTML = "";

  createOrderPaypal().then(orderID => {
    paypal.Buttons({
      createOrder: () => orderID,
      onApprove: (data, actions) => {
        capturarOrdenPaypal(data.orderID);
        cerrarModalPago();
      }
    }).render('#paypal-button-container');
  });
}

function cerrarModalPago() {
  document.getElementById("modalPagoPaypal").classList.remove("activo");
}


function cerrarModalPago() {
    document.getElementById("modalPagoPaypal").style.display = "none";
}
function cerrarModal() {
    document.getElementById("modalPago").style.display = "none";
    document.querySelector(".boton-confirmar").style.display = "none";

    seleccion = null;
    document.querySelectorAll(".opcion").forEach(op => op.classList.remove("seleccionada"));
}

window.addEventListener("click", function(e) {
  const modal = document.getElementById("modalPagoPaypal");
  if (e.target === modal) {
    cerrarModalPago();
  }
});
