




// Definir la función showError
function showError(message) {
    console.error(message);
    // Aquí puedes agregar el código para mostrar el error al usuario, como una alerta o una notificación en la página.
  }
  let guardada = localStorage.getItem("date")
  access_token = localStorage.getItem("access_token")  
  console.log("entra en scriptt en archivo login.html y guarda la fecha: ",guardada)//muestra localStorage
  // console.log("entra en scriptt en archivo login.html y guarda la token: ",tokenGuardado)//muestra localStorage    
  if (!access_token || tokenExpirado(access_token)) {
  // Obtener los tokens desde el diccionario de contexto de Flask
  if (typeof tokens !== 'undefined') {
    access_token = "{{ tokens[0] }}";
    const refresh_token = "{{ tokens[1] }}";
    correo_electronico = "{{ tokens[2] }}";
    const expiry_timestamp = "{{ tokens[3] }}";  // Marca de tiempo de expiración
    const roll = "{{ tokens[4] }}";
    const cuenta = "{{ tokens[5] }}";
    const selector = "{{ tokens[6] }}";
    const usuario = "{{ tokens[7] }}";
    const usuario_id = "{{ tokens[8] }}";
  
  
    // Almacenar los tokens y la marca de tiempo de expiración en el localStorage
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    localStorage.setItem("correo_electronico", correo_electronico);
    localStorage.setItem("expiry_timestamp", expiry_timestamp);
    localStorage.setItem("roll",roll);
    localStorage.setItem("cuenta",cuenta);
    localStorage.setItem("selector",selector);
    localStorage.setItem("usuario",usuario);
    localStorage.removeItem('usuario_id');
    localStorage.setItem("usuario_id",usuario_id);
   }
  }else {
  // Token válido, usarlo para la solicitud AJAX
  //document.getElementById("access_token").value = access_token;
  }
  
  // Función para verificar si el token ha expirado
  function tokenExpirado(token) {
  const expiry_timestamp = localStorage.getItem("expiry_timestamp");
  if (!expiry_timestamp) {
    return true;  // No se encontró la marca de tiempo de expiración, considerar expirado
  }
  const now_timestamp = new Date().getTime() / 1000;  // Convertir a segundos
  return now_timestamp >= expiry_timestamp;
  }
  /////////////////////// en esta seccion llama para ver
  var token = localStorage.getItem('access_token');
  if (tokenExpirado(token)) {
  // Almacenar los nuevos tokens en el localStorage
  
  localStorage.setItem("refresh_token", response.refresh_token);
  localStorage.setItem("correo_electronico", correo_electronico);
  localStorage.setItem("expiry_timestamp", response.expiry_timestamp);
  
  // Usar el nuevo access_token para la solicitud AJAX
  document.getElementById("token").value = response.access_token;
  console.log("Se ha obtenido un nuevo token exitosamente.");
  }
  else {
  console.log("No se pudo obtener un nuevo token.");
  }
  
  
  
  ///////////////////// en esta parte se llama para el logeo autmatico en el broker////////////////
  
   
      // Obtener el token del localStorage
     
      var refresh_token = localStorage.getItem('refresh_token');
      correo_electronico = localStorage.getItem('correo_electronico');
      var cuenta = localStorage.getItem("cuenta");
      var usuario = localStorage.getItem("usuario");
      var simuladoOproduccion = localStorage.getItem("selector");
      
     /* if (access_token) { // Verificar si el token existe en el localStorage
        // Enviar una solicitud a la ruta Flask y pasar el token como parte del cuerpo de la solicitud en formato JSON
        $.ajax({
          type: "POST",
          url: "{{ url_for('get_login.loginExtAutomatico') }}",
          contentType: "application/json",
          data: JSON.stringify({
                                'rutaDeLogeo':'Home',
                                'access_token': access_token,
                                'refresh_token':refresh_token,
                                'correo_electronico':correo_electronico,
                                'cuenta':cuenta,
                                'usuario':usuario,
                                'simuladoOproduccion':simuladoOproduccion
  
                              }),
          success: function(response) {
            if (response.redirect) {
              window.location.href = response.redirect;
            } else {
              // handle error
              showError("No se pudo redirigir al usuario se puede haber vencido el token loguee nuevamente");
            }
          },
          error: function(error) {
            // handle error
            showError("Hubo un error en la solicitud AJAX");
          }
        });
      }*/
    
  
  
  
  
  
  
      var accesstoken;
      var refreshtoken;
      var usuario1;
      
      // Obtener los tokens de localStorage y realizar la solicitud fetch
      function obtenerTokens() {
        accesstoken = localStorage.getItem('access_token');
        correo_electronico = localStorage.getItem('correo_electronico');
        refreshtoken = localStorage.getItem('refresh_token');
        usuario1 = localStorage.getItem('usuario');
        fetch('https://ipapi.co/json/')
          .then(response => response.json())
          .then(data => {
            const ip = data.ip;
            console.log(ip);
            console.log(correo_electronico);
            console.log(usuario1);
            localStorage.setItem('ip', ip);
      
            if (ip) {
              try {
                // Enviar una solicitud a la ruta Flask y pasar el token como parte del cuerpo de la solicitud en formato JSON
                $.ajax({
                  type: "POST",
                  url: "{{ url_for('media_e_mail.save_ip') }}",
                  contentType: "application/json",
                  data: JSON.stringify({ 'ip': ip, 'accesstoken': accesstoken, 'correo_electronico': correo_electronico, 'usuario1': usuario1 }),
                  success: function (response) {
                    if (response.redirect) {
                      window.location.href = response.redirect;
                    } else {
                      showError("No se pudo redirigir media_e_mail.save_ip");
                    }
                  },
                  error: function (error) {
                    // handle error
                    showError("Hubo un error en la solicitud AJAX");
                  }
                });
              } catch (error) {
                showError("Se produjo un error inesperado");
              }
            }
          })
          .catch(error => console.error(error));
      
      }
      
      // Llamar a la función obtenerTokens
      //obtenerTokens();
  
  
  