let seleccion = null;

function abrirModal() {
  document.getElementById('modalPago').style.display = 'flex';
}

function cerrarModal() {
  document.getElementById('modalPago').style.display = 'none';
  document.querySelector('.boton-confirmar').style.display = 'none';

  seleccion = null;
  document.querySelectorAll('.opcion').forEach(op => op.classList.remove('seleccionada'));
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.opcion').forEach(opcion => {
    opcion.addEventListener('click', () => {
      document.querySelectorAll('.opcion').forEach(o => o.classList.remove('seleccionada'));
      opcion.classList.add('seleccionada');
      seleccion = opcion.dataset.opcion;

      // Mostrar botón de confirmar
      document.querySelector('.boton-confirmar').style.display = 'block';
    });
  });
});


function confirmarPago() {
  if (!seleccion) {
    alert('Por favor, seleccioná una opción antes de continuar.');
    return;
  }
 

  switch (seleccion) {
        case 'paypal':
          // alert('Iniciando pago con PayPal...');

            abrirModalPago();
        break;


      case 'reserva':
        const formCliente = document.getElementById('form-cliente-pedido');

        if (formCliente) {
          const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
          formCliente.dispatchEvent(submitEvent);
        } else {
          alert('Formulario de cliente no disponible.');
        } 
      // Lógica personalizada
      break;

    case 'mercado_pago':
      const formMercadoPago = document.querySelector('.pagoPedidoForm');

     // if (formMercadoPago) {
        const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
        formMercadoPago.dispatchEvent(submitEvent);
     // } else {
     //   alert('No está disponible el pago online.');
      //}
      break;

    case 'reservaCita':
      debugger;
     
       const datosCliente = document.getElementById('datosCliente');
       console.log(datosCliente);
       modificarDatosClienteReserva(datosCliente,'reservaCita'); 





      // const calendlyData = document.getElementById('calendlyModal');


      //if (calendlyData) {
     //       const modalCalendly = new bootstrap.Modal(document.getElementById('calendlyModal'));
     //       modalCalendly.show();
     // } else {
        // Oculta el botón de "Reservar sin pagar"
      //    const reservaOpcion = document.getElementById('opcion-reserva');
       //   if (reservaOpcion) {
        //    reservaOpcion.style.display = 'none';
        //  }
      //}

     
      break;
  }

  cerrarModal();
}


async function modificarDatosClienteReserva(datosCliente, tipo) {



  if (!datosCliente) {
    alert('No se encontraron los datos del cliente.');
    return false;
  }

  // Scope local: de la card que contiene estos inputs
  const card = datosCliente.closest('.card') || document;

  const pick = (sel) => {
    const el = card.querySelector(sel);
    return el ? el.value.trim() : '';
  };

  // Token
  const access_token_btn_pocesarPedido = localStorage.getItem('access_token');
  if (!access_token_btn_pocesarPedido) {
    alert('No hay access token. Volvé a iniciar sesión.');
    return false;
  }

  // Datos del cliente
  const nombreCliente     = pick('#nombreCliente');
  const apellidoCliente   = pick('#apellidoCliente');
  const direccionCliente  = pick('#direccionCliente');
  const telefonoCliente   = pick('#telefonoCliente');
  const emailCliente      = pick('#emailCliente');
  const comentariosCliente= pick('#comentariosCliente');

  // Hidden del pedido (OJO: pueden existir dos formularios con mismos IDs; por eso scoping)
  const ambito_pagoPedido = pick('#ambito_pagoPedido');
  const pedido_data_json  = pick('#pedido_data_json_pagoPedido');
  const cluster_pedido    = pick('#cluster_pedido');
  const costo_base        = parseFloat(pick('#costo_base')) || 0;
  const porcentaje_retorno= parseFloat(pick('#porcentaje_retorno')) || 0;

  const final_price = +(costo_base - (costo_base * porcentaje_retorno / 100)).toFixed(2);

  if(tipo !== 'reservaCita' && tipo !== 'reserva') {
    if (final_price == 0) {
      alert('El precio final no puede ser cero para este tipo de pago.');
      return false;
      }
    }
   

  const preference_data = {
    nombreCliente,
    apellidoCliente,
    direccionCliente,
    telefonoCliente,
    emailCliente,
    comentariosCliente,
    ambito_pagoPedido,
    costo_base,
    porcentaje_retorno,
    final_price,
    pedido_data_json,
    cluster_pedido,
    tipo: 'reserva' // útil si en backend distinguís reserva vs pago
  };

  try {
    const resp = await $.ajax({
      url: '/productosComerciales_pedidos_process_order/',
      type: 'POST',
      contentType: 'application/json',
      headers: { 'Authorization': 'Bearer ' + access_token_btn_pocesarPedido },
      data: JSON.stringify(preference_data)
    });

    // Feedback
    alert('Pedido procesado correctamente');

    // Limpiar campos visibles (scopeado a esta card)
    ['#nombreCliente','#apellidoCliente','#direccionCliente','#telefonoCliente','#emailCliente','#comentariosCliente']
      .forEach(sel => {
        const el = card.querySelector(sel);
        if (el) el.value = '';
      });

    // Si tu backend devuelve algo útil, podés usarlo:
    // if (resp?.init_point) window.location.href = resp.init_point;

    return true;
  } catch (err) {
    console.error('Error procesando pedido:', err);
    alert('Hubo un error al procesar el pedido.');
    return false;
  }
}




