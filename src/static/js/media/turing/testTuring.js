document.getElementById("respuestaUltimaPregunta").addEventListener("click", function() {
    // Abre el modal cuando se hace clic en el encabezado
    new bootstrap.Modal(document.getElementById("modalrespuestaUltimaPregunta")).show();
});

document.getElementById("enviarRespuestaBtn").addEventListener("click", function() {
    // Obtener la respuesta del input
    var respuesta = document.getElementById("respuestaInput").value;

    if (respuesta.trim() === "") {
        alert("Por favor, ingresa una respuesta.");
        return;
    }

    // Hacer la petición AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "ruta_del_servidor", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");

    // Manejo de la respuesta
    xhr.onload = function() {
        if (xhr.status === 200) {
            // Acción cuando la respuesta del servidor es exitosa
            alert("Respuesta enviada correctamente.");
            // Puedes hacer algo adicional aquí (como limpiar el campo de input)
            document.getElementById("respuestaInput").value = "";
            // Cerrar el modal
            var modal = bootstrap.Modal.getInstance(document.getElementById("modalrespuestaUltimaPregunta"));
            modal.hide();
        } else {
            // Acción en caso de error
            alert("Hubo un error al enviar la respuesta.");
        }
    };

    // Enviar la respuesta
    xhr.send("respuesta=" + encodeURIComponent(respuesta));
});






// Obtener el botón que abre el modal
document.getElementById('btnAbrirModalLastAnswer').addEventListener('click', function() {
    // Mostrar el modal LasAnswersModal usando Bootstrap JS
    var LasAnswersModal = new bootstrap.Modal(document.getElementById('LasAnswersModal'));
    LasAnswersModal.show();
  });
  
 
 
 
 
 
 
 // Cuando se hace clic en el botón "Enviar"
  
 document.getElementById('enviarPreguntaBtn').onclick = function() {
    var pregunta = document.getElementById('preguntaInput').value;  // Obtiene el valor del input

    // Verifica si la pregunta no está vacía
    if (pregunta.trim() !== '') {
      // Realiza la solicitud AJAX
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/ruta-a-tu-endpoint", true); // Cambia "/ruta-a-tu-endpoint" a la ruta de tu servidor
      xhr.setRequestHeader("Content-Type", "application/json");

      // Envía la pregunta al servidor como JSON
      xhr.send(JSON.stringify({ pregunta: pregunta }));

      // Cuando la solicitud termine, procesa la respuesta
      xhr.onload = function() {
        if (xhr.status === 200) {
          // Si la respuesta fue exitosa, puedes manejar la respuesta aquí
          alert("Pregunta enviada exitosamente.");
          // Puedes también limpiar el input
          document.getElementById('preguntaInput').value = '';
        } else {
          alert("Hubo un error al enviar la pregunta.");
        }
      };
    } else {
      alert("Por favor, escribe una pregunta.");
    }
  };    




















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









