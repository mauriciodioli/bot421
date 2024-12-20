

let respuestaSeleccionada = ''; // Variable para almacenar la respuesta seleccionada

// Evento para el botón "Maquina"
document.getElementById('btnMaquina').addEventListener('click', function() {
  respuestaSeleccionada = 'Maquina'; // Almacenar la respuesta seleccionada
  // Mostrar el modal de confirmación
  var confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
  confirmModal.show();
});

// Evento para el botón "Humano"
document.getElementById('btnHumano').addEventListener('click', function() {
  respuestaSeleccionada = 'Humano'; // Almacenar la respuesta seleccionada
  // Mostrar el modal de confirmación
  var confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
  confirmModal.show();
});

// Evento para confirmar la respuesta
document.getElementById('confirmarRespuesta').addEventListener('click', function() {
  // Llamar a la función AJAX para enviar la respuesta seleccionada
  enviarRespuesta(respuestaSeleccionada);

  // Cerrar el modal después de confirmar
  var confirmModal = new bootstrap.Modal(document.getElementById('confirmModal'));
  confirmModal.hide();
});

// Función para enviar la respuesta por AJAX
function enviarRespuesta(respuesta) {
  // Realizar la llamada AJAX para enviar la respuesta al servidor
  console.log('Enviando respuesta: ' + respuesta);

  // Aquí puedes agregar tu código AJAX (con fetch, XMLHttpRequest, o cualquier librería de tu preferencia)
  // Ejemplo básico de una solicitud AJAX con fetch:
  fetch('/ruta/a/tu/servidor', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ respuesta: respuesta })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Respuesta del servidor:', data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
}
