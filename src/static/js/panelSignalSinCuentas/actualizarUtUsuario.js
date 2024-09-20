function saveUtUsuario() {
  // Obtener el valor del input
  var ut_usuario = $('#idUtInput').val();
  
  // Guardar el valor en localStorage
  localStorage.setItem('ut_usuario', ut_usuario);
   // Intentar obtener el elemento del DOM
   var utUsuarioElement = document.getElementById('ut_usuario');

   // Verificar si el elemento existe antes de modificarlo
   if (utUsuarioElement) {
     utUsuarioElement.textContent = 'Esperando actualización: ' + ut_usuario;
     utUsuarioElement.style.color = 'yellow';
   } else {
     console.error("El elemento con el id 'ut_usuario' no existe.");
   }

  // Obtener otros valores de localStorage si es necesario
  var access_token = localStorage.getItem('access_token');
  var refresh_token = localStorage.getItem('refresh_token');
  var selector = localStorage.getItem('selector');
  var usuario_id = localStorage.getItem('usuario_id');
  var cuenta  = localStorage.getItem('cuenta');
  
  // URL del endpoint
  var url = '/cuentas-cuentaUsuarioBroker-actualizarUt/';
  
  // Realizar la solicitud AJAX
  $.ajax({
      type: 'POST',
      url: url,
      data: {
          ut_usuario: ut_usuario,
          access_token: access_token,  // Incluye otros datos si es necesario
          refresh_token: refresh_token,
          selector: selector,
          usuario_id: usuario_id,
          cuenta: cuenta
      },
      success: function(response) {
        // Manejar la respuesta exitosa
        if (response.message === 'Tiene cuenta, no puede modificar desde aquí' && response.status === 'error') {
            alert(response.message);
            $('#UtUsuarioModal').modal('hide');
            // Asignar el valor de 0 a la Unidad de Tradeo
            $('#ut_usuario').text('Unidad de Tradeo: 0');
            // Opcionalmente, mostrar un mensaje o notificación
            alert(response.message);
        } else {
          // Manejar la respuesta exitosa
          console.log("UT actualizado con éxito:", response);
          // Opcionalmente, esconder el modal
          $('#UtUsuarioModal').modal('hide');
        }
      },
      error: function(xhr, status, error) {
          // Manejar errores
          console.error("Error al actualizar UT:", error);
      }
  });
}
