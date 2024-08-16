function saveUtUsuario() {
  // Obtener el valor del input
  var ut_usuario = $('#idUtInput').val();
  
  // Guardar el valor en localStorage
  localStorage.setItem('ut_usuario', ut_usuario);
  
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
          console.log("UT actualizado con éxito:", response);
          // Opcionalmente, esconder el modal
          $('#UtUsuarioModal').modal('hide');
      },
      error: function(xhr, status, error) {
          // Manejar errores
          console.error("Error al actualizar UT:", error);
      }
  });
}
