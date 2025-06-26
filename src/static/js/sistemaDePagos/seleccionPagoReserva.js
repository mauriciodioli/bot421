<<<<<<< HEAD
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
           alert('Iniciando pago con PayPal...');

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
     
       const calendlyData = document.getElementById('calendly-data');

      if (calendlyData) {
            const modalCalendly = new bootstrap.Modal(document.getElementById('calendlyModal'));
            modalCalendly.show();
      } else {
        // Oculta el botón de "Reservar sin pagar"
          const reservaOpcion = document.getElementById('opcion-reserva');
          if (reservaOpcion) {
            reservaOpcion.style.display = 'none';
          }
      }

     
      break;
  }

  cerrarModal();
}
=======
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
           alert('Iniciando pago con PayPal...');

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
     
       const calendlyData = document.getElementById('calendly-data');

      if (calendlyData) {
            const modalCalendly = new bootstrap.Modal(document.getElementById('calendlyModal'));
            modalCalendly.show();
      } else {
        // Oculta el botón de "Reservar sin pagar"
          const reservaOpcion = document.getElementById('opcion-reserva');
          if (reservaOpcion) {
            reservaOpcion.style.display = 'none';
          }
      }

     
      break;
  }

  cerrarModal();
}
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
