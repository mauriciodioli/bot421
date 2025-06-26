<<<<<<< HEAD
// service-worker.js

// Evento install: se dispara cuando se registra el Service Worker
self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
  });
  
  // Evento activate: se dispara cuando el Service Worker se activa
  self.addEventListener('activate', function(event) {
    console.log('Service Worker activado');
  });
  
  // Evento fetch: se dispara cuando la aplicación solicita recursos al servidor
  self.addEventListener('fetch', function(event) {
    // No es necesario manejar fetch en este caso si solo se desea actualización periódica
  });
  
  // Evento periodicSync: se dispara para realizar actualizaciones en segundo plano
  self.addEventListener('periodicsync', function(event) {
    if (event.tag === 'actualizar-tabla') {
      console.log('Ejecutando actualización de tabla en segundo plano');
      event.waitUntil(actualizarTabla()); // Llama a la función de actualización de tabla
    }
  });
  
  // Función para actualizar la tabla
  function actualizarTabla() {
    // Obtener las filas de la tabla
    var tableBody = document.getElementById('tableBody');
    var rows = tableBody.getElementsByTagName('tr');
    var filasTablaDatos = [];
  
    // Leer datos de cada fila de la tabla
    for (var i = 1; i < rows.length; i++) { // Empieza en 1 para saltar el encabezado
      var cells = rows[i].getElementsByTagName('td');
      var datosFila = [];
      for (var j = 0; j < cells.length; j++) {
        datosFila.push(cells[j].innerText);
      }
      filasTablaDatos.push(datosFila);
    }
  
    // Enviar notificaciones a Telegram si está activado entre las 14:00 y las 20:00
    var ahora = new Date();
    var hora = ahora.getHours();
    if (hora >= 14 && hora < 20) {
      enviarNotificacionesTelegram(filasTablaDatos);
    }
  }
  
  // Función para enviar notificaciones a Telegram
  function enviarNotificacionesTelegram(filasTablaDatos) {
    var notificacionTelegram = localStorage.getItem('notificacionTelegram');
  
    // Verificar si notificacionTelegram es 'True'
    if (notificacionTelegram == 'True') {
      var paisSeleccionado = localStorage.getItem('paisSeleccionado');
      var access_token = localStorage.getItem('access_token');
      var selector = localStorage.getItem('selector');
      var idtelegram = localStorage.getItem('idtelegram');
  
      // Iterar sobre las filas de datos y enviar cada fila por AJAX
      filasTablaDatos.forEach(function(fila) {
        var formData = {
          access_token: access_token,
          symbol: fila[1], // Ajustar el índice según la posición de symbol en tu fila
          ut: fila[5], // Ajustar el índice según la posición de ut en tu fila
          senial: fila[3], // Ajustar el índice según la posición de senial en tu fila
          correo_electronico: document.getElementById('correo_electronico').value,
          paisSeleccionado: paisSeleccionado,
          idtelegram: idtelegram,
          selector: selector
        };
  
        // Realizar la solicitud AJAX
        $.ajax({
          type: "POST",
          url: '/envio_notificacion_tlegram_desde_seniales_sin_cuenta/',
          contentType: 'application/json', // Asegúrate de que el tipo de contenido sea JSON
          data: JSON.stringify(formData), // Convertir formData a JSON
          success: function(response) {
            console.log("Respuesta del servidor:", response);
            // Manejar la respuesta del servidor si es necesario
          },
          error: function(error) {
            console.error("Error al enviar datos por AJAX:", error);
            // Manejar errores si es necesario
          }
        });
      });
    } else {
      // Manejar el caso cuando notificacionTelegram no es 'True'
      console.log("La notificación no está activada.");
    }
  }
  
=======
// service-worker.js

// Evento install: se dispara cuando se registra el Service Worker
self.addEventListener('install', function(event) {
    console.log('Service Worker instalado');
  });
  
  // Evento activate: se dispara cuando el Service Worker se activa
  self.addEventListener('activate', function(event) {
    console.log('Service Worker activado');
  });
  
  // Evento fetch: se dispara cuando la aplicación solicita recursos al servidor
  self.addEventListener('fetch', function(event) {
    // No es necesario manejar fetch en este caso si solo se desea actualización periódica
  });
  
  // Evento periodicSync: se dispara para realizar actualizaciones en segundo plano
  self.addEventListener('periodicsync', function(event) {
    if (event.tag === 'actualizar-tabla') {
      console.log('Ejecutando actualización de tabla en segundo plano');
      event.waitUntil(actualizarTabla()); // Llama a la función de actualización de tabla
    }
  });
  
  // Función para actualizar la tabla
  function actualizarTabla() {
    // Obtener las filas de la tabla
    var tableBody = document.getElementById('tableBody');
    var rows = tableBody.getElementsByTagName('tr');
    var filasTablaDatos = [];
  
    // Leer datos de cada fila de la tabla
    for (var i = 1; i < rows.length; i++) { // Empieza en 1 para saltar el encabezado
      var cells = rows[i].getElementsByTagName('td');
      var datosFila = [];
      for (var j = 0; j < cells.length; j++) {
        datosFila.push(cells[j].innerText);
      }
      filasTablaDatos.push(datosFila);
    }
  
    // Enviar notificaciones a Telegram si está activado entre las 14:00 y las 20:00
    var ahora = new Date();
    var hora = ahora.getHours();
    if (hora >= 14 && hora < 20) {
      enviarNotificacionesTelegram(filasTablaDatos);
    }
  }
  
  // Función para enviar notificaciones a Telegram
  function enviarNotificacionesTelegram(filasTablaDatos) {
    var notificacionTelegram = localStorage.getItem('notificacionTelegram');
  
    // Verificar si notificacionTelegram es 'True'
    if (notificacionTelegram == 'True') {
      var paisSeleccionado = localStorage.getItem('paisSeleccionado');
      var access_token = localStorage.getItem('access_token');
      var selector = localStorage.getItem('selector');
      var idtelegram = localStorage.getItem('idtelegram');
  
      // Iterar sobre las filas de datos y enviar cada fila por AJAX
      filasTablaDatos.forEach(function(fila) {
        var formData = {
          access_token: access_token,
          symbol: fila[1], // Ajustar el índice según la posición de symbol en tu fila
          ut: fila[5], // Ajustar el índice según la posición de ut en tu fila
          senial: fila[3], // Ajustar el índice según la posición de senial en tu fila
          correo_electronico: document.getElementById('correo_electronico').value,
          paisSeleccionado: paisSeleccionado,
          idtelegram: idtelegram,
          selector: selector
        };
  
        // Realizar la solicitud AJAX
        $.ajax({
          type: "POST",
          url: '/envio_notificacion_tlegram_desde_seniales_sin_cuenta/',
          contentType: 'application/json', // Asegúrate de que el tipo de contenido sea JSON
          data: JSON.stringify(formData), // Convertir formData a JSON
          success: function(response) {
            console.log("Respuesta del servidor:", response);
            // Manejar la respuesta del servidor si es necesario
          },
          error: function(error) {
            console.error("Error al enviar datos por AJAX:", error);
            // Manejar errores si es necesario
          }
        });
      });
    } else {
      // Manejar el caso cuando notificacionTelegram no es 'True'
      console.log("La notificación no está activada.");
    }
  }
  
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
  