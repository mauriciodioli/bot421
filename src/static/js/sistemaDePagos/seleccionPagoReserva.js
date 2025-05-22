let seleccion = null;

function abrirModal() {
  document.getElementById('modalPago').style.display = 'flex';
}

function cerrarModal() {
  document.getElementById('modalPago').style.display = 'none';
  seleccion = null;
  document.querySelectorAll('.opcion').forEach(op => op.classList.remove('seleccionada'));
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.opcion').forEach(opcion => {
    opcion.addEventListener('click', () => {
      document.querySelectorAll('.opcion').forEach(o => o.classList.remove('seleccionada'));
      opcion.classList.add('seleccionada');
      seleccion = opcion.dataset.opcion;
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
      // Lógica personalizada
      break;
    case 'mercado_pago':
      alert('Iniciando pago con Mercado Pago...');
      break;
    case 'reserva':
      alert('Reserva sin pago confirmada.');
      break;
  }

  cerrarModal();
}
