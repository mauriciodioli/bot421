
document.addEventListener('DOMContentLoaded', function() {


    document.getElementById('splash').style.display = 'block';
    //{% if cuenta is defined %}
    // Acceder a los tokens desde el diccionario de contexto de Flask
    var cuenta = "{{ cuenta[0] }}";
    var usuario = "{{ cuenta[1] }}";
    var selector = "{{ cuenta[2] }}";
   
    console.log("probanodo",cuenta)
    console.log(usuario)
    console.log(selector)
    // Almacenar los tokens en el localStorage
    localStorage.setItem("cuenta", cuenta);
    localStorage.setItem("usuario", usuario);
    localStorage.setItem("selector", selector);
    //{% endif %}
    document.addEventListener('click', function(event) {
      if (event.target && event.target.id == "boton-despues-carga-tabla") {
          document.getElementById('splash').style.display = 'block';
          access_token = localStorage.getItem('access_token');
          var cuentaEnvioAjax = localStorage.getItem('correo_electronico');
          var symbol = event.target.dataset.symbol;
          var senial = event.target.dataset.senial;      
          var ut = event.target.dataset.ut;
          var paisS = localStorage.getItem('paisSeleccionado');
          
          // Llenar los campos ocultos en el formulario del modal
          document.getElementById('symbol').value = symbol;
          document.getElementById('senial').value = senial;     
          document.getElementById('ut').value = ut;
          document.getElementById('access_token').value = access_token;
          document.getElementById('correo_electronico').value = cuentaEnvioAjax;
          document.getElementById('paisSeleccionado').value = paisS;
          // Cerrar el modal
          $('#confirmModal').modal('hide');
      }
    });
  
    // Llama a la función de actualización inicial
    window.addEventListener('load', function() {
      updateTable();
    });
  
    function updateTable() {
      // Guarda los elementos visibles antes de la actualización
      // var elementosAntes = obtenerElementos();
  
    // var cambiosAntes = compararCambios();
      // Realizar una solicitud AJAX para obtener los nuevos datos
      
      var paisSeleccionado = localStorage.getItem('paisSeleccionado');
      var usuario_id = localStorage.getItem('usuario_id');
      var access_token = localStorage.getItem('access_token');
      var selector = localStorage.getItem('selector');
      var account = 'vacio'
      var xhr = new XMLHttpRequest();
     
      var url = '/panel_control_atomatico/'+paisSeleccionado+'/'+usuario_id+'/'+access_token+'/'+account+'/'+selector+'/';
      
      xhr.open('GET', url, true);
      //  encabezado Content-Type
      xhr.setRequestHeader('Content-Type', 'application/json');
  
      xhr.onload = function() {
        if (xhr.status >= 200 && xhr.status < 400) {
          // La solicitud fue exitosa, actualiza la tabla  
         
          var response = JSON.parse(xhr.responseText);
        
          var tableBody = document.getElementById('signalTable').getElementsByTagName('tbody')[0];
          tableBody.innerHTML = ''; // Limpiar el contenido actual de la tabla
  
          
        
        //  var filasCambiadas = comparaFilas(elementosAntes, response);
          //console.log(filasCambiadas);
  
          // Crea una fila de encabezado
          var headerRow = document.createElement('tr');
          // Agrega encabezados a cada columna
          headerRow.innerHTML = `
          <thead>           
            <tr>
              <th>Orden</th>
              <th>Symbol</th>
              <th>Type</th>
              <th>Signal</th>
              <th>In Progress</th>
              <th>Ut</th>
              <th>Operated</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>           
            
          `;
          // Agrega la fila de encabezado a la tabla
          tableBody.appendChild(headerRow);
          for (var i = 0; i < response.datos.length; i++) {
  
            var dato = response.datos[i];
          
          
            console.log('dato[1] ',dato[1],'dato[2] ',dato[2],'dato[3] ',dato[3],'dato[4] ',dato[4],'dato[5] ',dato[5],'dato[6] ',dato[6],'dato[7] ',dato[7],'dato[8] ,',dato[8],'dato[9] ',dato[9],'dato[1] ',dato[10])
           
            if (
                (dato[1] == 'ARG' || dato[1] == 'CEDEAR') &&
                (dato[2] == 'LONG_' || (dato[2] != 'SHORT'))
               ) {
                      if (dato[4] === 'OPEN.'  && dato[8] === null){
                        if (Number(dato[3]) > 0) {                                          
                        //if (dato[4] !== dato[8]) {
                          //if (dato[7] !== null) {
                            // var campana = document.getElementById('Campana');
                            // campana.play();
                         //       mostrarNotificacion(dato);
                         //   }
                            var row = document.createElement('tr');
                            var numeroDeOrden = i + 1; // Empieza desde 1
                            var filaId = 'fila-' + i;
                            row.setAttribute('id', filaId);
                            row.innerHTML = `
                              <td>${numeroDeOrden}</td>
                              <td>${dato[0].replace('MERV - XMEV -', '')}</td>
                              <td>${dato[1]}</td>
                              <td>${dato[4]}</td>
                              <td>${dato[2]}</td>
                              <td>${dato[3]}</td>
                              <td>${dato[9]}</td>
                              <td>${dato[8]}</td>
                              <td>
                                <div class="form-group">
                                  <input type="hidden" name="symbol" placeholder="escribe simbolo" value="${dato[0]}" class="form-control">
                                </div>
                                <div class="form-group">
                                  <input type="hidden" name="senial" value="{{ senial }}">
                                  <input type="hidden" name="ut" value="{{ ut }}">
                                  <input type="hidden" id="datoValor" class="form-control">
                                  ${
                                    dato[4] == 'OPEN.'
                                      ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-success btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                      : ''
                                  }
                                  ${
                                    dato[4] == 'closed.'
                                      ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-danger btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                      : ''
                                  }
                                </div>
                              </td>
                            `;
                            tableBody.appendChild(row);
                        }
  
                      }
  
  
                      
                   if (dato[4] === 'closed.' && dato[9] !== null) {    
                                                              
                        if (dato[4] !== dato[9]) {
                          if (Number(dato[3]) > 0) {
                          //if (dato[7] !== null) {
                            // var campana = document.getElementById('Campana');
                            // campana.play();
                          //      mostrarNotificacion(dato);
                         //   }
                            var row = document.createElement('tr');
                            var numeroDeOrden = i + 1; // Empieza desde 1
                            var filaId = 'fila-' + i;
                            row.setAttribute('id', filaId);
                            row.innerHTML = `
                              <td>${numeroDeOrden}</td>
                              <td>${dato[0].replace('MERV - XMEV -', '')}</td>
                              <td>${dato[1]}</td>
                              <td>${dato[4]}</td>
                              <td>${dato[2]}</td>
                              <td>${dato[3]}</td>
                              <td>${dato[9]}</td>
                              <td>${dato[8]}</td>
                              <td>
                                <div class="form-group">
                                  <input type="hidden" name="symbol" placeholder="escribe simbolo" value="${dato[0]}" class="form-control">
                                </div>
                                <div class="form-group">
                                  <input type="hidden" name="senial" value="{{ senial }}">
                                  <input type="hidden" name="ut" value="{{ ut }}">
                                  <input type="hidden" id="datoValor" class="form-control">
                                  ${
                                    dato[4] == 'OPEN.'
                                      ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-success btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                      : ''
                                  }
                                  ${
                                    dato[4] == 'closed.'
                                      ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-danger btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                      : ''
                                  }
                                </div>
                              </td>
                            `;
                            tableBody.appendChild(row);
                        }
                       }
                      }
  
                  
                    
                  }
            
                  if (
                    (dato[1] === 'USA') &&
                    (dato[2] === 'LONG_' || (dato[2] === 'SHORT'))
                   ) {
                          if (dato[4] === 'OPEN.'  && dato[9] === null){
                                                                        
                            //if (dato[4] !== dato[8]) {
                            //  if (dato[7] !== null) {
                                // var campana = document.getElementById('Campana');
                                // campana.play();
                            //        mostrarNotificacion(dato);
                            //    }
                                var row = document.createElement('tr');
                                var numeroDeOrden = i + 1; // Empieza desde 1
                                var filaId = 'fila-' + i;
                                row.setAttribute('id', filaId);
                                row.innerHTML = `
                                  <td>${numeroDeOrden}</td>
                                  <td>${dato[0].replace('MERV - XMEV -', '')}</td>
                                  <td>${dato[1]}</td>
                                  <td>${dato[4]}</td>
                                  <td>${dato[2]}</td>
                                  <td>${dato[3]}</td>
                                  <td>${dato[9]}</td>
                                  <td>${dato[8]}</td>
                                  <td>
                                    <div class="form-group">
                                      <input type="hidden" name="symbol" placeholder="escribe simbolo" value="${dato[0]}" class="form-control">
                                    </div>
                                    <div class="form-group">
                                      <input type="hidden" name="senial" value="{{ senial }}">
                                      <input type="hidden" name="ut" value="{{ ut }}">
                                      <input type="hidden" id="datoValor" class="form-control">
                                      ${
                                        dato[4] == 'OPEN.'
                                          ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-success btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                          : ''
                                      }
                                      ${
                                        dato[4] == 'closed.'
                                          ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-danger btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                          : ''
                                      }
                                    </div>
                                  </td>
                                `;
                                tableBody.appendChild(row);
                            }
      
                         // }
      
      
                          
                       if (dato[4] === 'closed.' && dato[9] !== null) {    
                                                                  
                            if (dato[4] !== dato[9]) {
                             // if (dato[7] !== null) {
                                // var campana = document.getElementById('Campana');
                                // campana.play();
                                   // mostrarNotificacion(dato);
                             //   }
                                var row = document.createElement('tr');
                                var numeroDeOrden = i + 1; // Empieza desde 1
                                var filaId = 'fila-' + i;
                                row.setAttribute('id', filaId);
                                row.innerHTML = `
                                  <td>${numeroDeOrden}</td>
                                  <td>${dato[0].replace('MERV - XMEV -', '')}</td>
                                  <td>${dato[1]}</td>
                                  <td>${dato[4]}</td>
                                  <td>${dato[2]}</td>
                                  <td>${dato[3]}</td>
                                  <td>${dato[9]}</td>
                                  <td>${dato[8]}</td>
                                  <td>
                                    <div class="form-group">
                                      <input type="hidden" name="symbol" placeholder="escribe simbolo" value="${dato[0]}" class="form-control">
                                    </div>
                                    <div class="form-group">
                                      <input type="hidden" name="senial" value="{{ senial }}">
                                      <input type="hidden" name="ut" value="{{ ut }}">
                                      <input type="hidden" id="datoValor" class="form-control">
                                      ${
                                        dato[4] == 'OPEN.'
                                          ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-success btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                          : ''
                                      }
                                      ${
                                        dato[4] == 'closed.'
                                          ? `<button id="boton-despues-carga-tabla" type="button" class="btn btn-danger btn-sm btn-block form-control" data-bs-toggle="modal" data-bs-target="#confirmModal" data-senial="${dato[4]}" data-symbol="${dato[0]}" data-ut="${dato[3]}">Submit</button>`
                                          : ''
                                      }
                                    </div>
                                  </td>
                                `;
                                tableBody.appendChild(row);
                            }
                           
                          }
      
                      
                        
                      }
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
            
            $(document).ready(function () {
              // Iterar sobre las filas de la tabla
              $('#signalTable tbody tr').each(function () {
                // Obtener el texto de la columna Signal
                var signalText = $(this).find('td:nth-child(4)').text().trim();
                var typeText = $(this).find('td:nth-child(3)').text().trim();
                var inProgres = $(this).find('td:nth-child(5)').text().trim();
                // Verificar si es OPEN o Closed y aplicar el color correspondiente
                if (signalText === 'OPEN.') {
                  $(this).find('td:nth-child(4)').css('color', 'green');
                } else if (signalText === 'closed.') {
                  $(this).find('td:nth-child(4)').css('color', 'red');
                }
            
                if (typeText === 'CEDEAR') {
                  $(this).find('td:nth-child(3)').css('color', 'brown ');
                } else if (typeText === 'ARG') {
                  $(this).find('td:nth-child(3)').css('color', 'cyan');
                }
            
                if (inProgres === 'SHORT') {
                  $(this).find('td:nth-child(5)').css('color', 'pink');
                } else if (inProgres === 'LONG_') {
                  $(this).find('td:nth-child(5)').css('color', 'cyan');
                }
                     
              });
            });
            
  
          
          }
        // Después de actualizar la tabla, puedes comparar los cambios nuevamente
        document.getElementById('splash').style.display = 'none';
        document.getElementById('contenido').style.display = 'block';
        //var cambiosDespues = compararCambios();
  
        //  var openChanged = cambiosDespues.openBefore - cambiosAntes.openBefore;
        //   var closedChanged = cambiosDespues.closedBefore - cambiosAntes.closedBefore;
  
        // console.log('Cambios en estado OPEN:', openChanged);
        //  console.log('Cambios en estado closed:', closedChanged);
        // Oculta las filas que no cambiaron
      
        } else {
          // Hubo un error en la solicitud
          showError('Error al obtener los datos: ' + xhr.statusText);
        }
      };
  
        xhr.onerror = function() {
        showError('Error de red al intentar obtener los datos');
      };
      //console.log('XHR:', xhr);
      //console.log('URL:', xhr.url);
      xhr.send();
    }
  
    // Llama a la función de actualización inicial/
    //updateTable();
  
  
   
    
  
  
  
  
  
  
  
  
  
    // Establece un intervalo para actualizar la tabla cada 5 minutos
    //setInterval(updateTable, 300000); // 300000 milisegundos = 5 minutos
    //setInterval(updateTable, 90000); // 90000 milisegundos = 1 minuto 30 segundos
    setInterval(updateTable, 420000); // 15 segundos
  
    // Definir la función showError
    function showError(message) {
      console.error('message');
      // Aquí puedes agregar el código para mostrar el error al usuario, como una alerta o una notificación en la página.
    }
  
    function compararCambios() {
      var openBefore = contarElementosOpen();
      var closedBefore = contarElementosClosed();
  
  
      return {
        openBefore: openBefore,
        closedBefore: closedBefore
      };
    }
  
    function contarElementosOpen() {
      var openCount = 0;
      var allTds = document.querySelectorAll('td:nth-child(4)');
      
      allTds.forEach(function(td) {
        if (td.textContent.includes("OPEN.")) {
          openCount++;
        }
      });
  
      return openCount;
    }
    function contarElementosClosed() {
      var closedCount = 0;
      var allTds = document.querySelectorAll('td:nth-child(4)');
      
      allTds.forEach(function(td) {
        if (td.textContent.includes("closed.")) {
          closedCount++;
        }
      });
  
      return closedCount;
    }
  
    function obtenerElementos() {
      var elementosVisibles = [];
      var filas = document.getElementById('signalTable').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
      
      for (var i = 0; i < filas.length; i++) {
        if (filas[i].style.display !== 'none') {
          elementosVisibles.push(filas[i]);
        }
      }
      console.log('Elementos visibles:', elementosVisibles);
      return elementosVisibles;
    }
  
    function comparaFilas(elementosAntes, response) {
      var filasCambiadas = [];
      
      // Itera sobre los elementos antes de la actualización
      elementosAntes.forEach(function(filaAntes) {
        var datoAntes = obtenerDatoDesdeFila(filaAntes);    
        var idAntes = datoAntes[0]; // Supongo que el primer elemento es un identificador único
        
        //console.log("idAntes:", idAntes);
          // Busca el mismo dato en la respuesta
          var datoDespues = response.datos.find(function(dato) {
            //console.log("dato[0]:", dato[0]);
            return dato[1] === idAntes;
          });
  
        // Si el dato ha cambiado, añádelo a la lista de filas cambiadas
        if (datoDespues && datoDespues[4] !== datoAntes[3]) {
          filasCambiadas.push(datoDespues);
          console.log("El dato ha cambiado:", datoDespues);
        }
      });
  
      return filasCambiadas;
    }
  
  
    function ocultarFilasNoCambiadas(elementosAntes) {
      var filas = document.getElementById('signalTable').getElementsByTagName('tbody')[0].getElementsByTagName('tr');
  
      for (var i = 0; i < filas.length; i++) {
        // Obtener el dato[3] de la fila actual
        var dato = obtenerDatoDesdeFila(filas[i]);
  
        // Verificar si el dato[3] ha cambiado
        if (!elementosAntes.includes(filas[i]) && dato[3] === '0') {
          filas[i].style.display = 'none';
        }
      }
    }
  
  
    function obtenerDatoDesdeFila(fila) {
      // Obtener los valores de cada celda de la fila
      
      var celdas = fila.getElementsByTagName('td');
      
      // Crear un array para almacenar los valores
      var dato = [];
      for (var j = 0; j < celdas.length; j++) {    
        dato.push(celdas[j].textContent.trim());    
      }
  
      return dato;
    }
  });
  
  
  
  
  
  $(document).ready(function(){
    $('#donationForm').submit(function(event){
        event.preventDefault(); // Evita que el formulario se envíe de manera convencional
  
        // Obtén los datos del formulario
        var formData = {
            costo_base: $('#costo_base').val(),
            porcentaje_retorno: $('#porcentaje_retorno').val()
        };
  
        // Crea los datos de la preferencia
        var preference_data = {
            items: [
                {
                    title: "Donacion de prueba",
                    quantity: 1,
                    unit_price: formData.costo_base
                }
            ],
            back_urls: {
                success: "https://89ae-190-225-182-66.ngrok-free.app/success",
                failure: "https://89ae-190-225-182-66.ngrok-free.app/failure",
                pending: "https://89ae-190-225-182-66.ngrok-free.app/pending"
            },
            notification_url: "https://89ae-190-225-182-66.ngrok-free.app/webhook",
            auto_return: "approved"
        };
  
        // Envía la solicitud AJAX
        $.ajax({
            url: '/create_order/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(preference_data),
            success: function(response) {
                // Redirige a la URL de inicialización de la preferencia
                window.location.href = response.init_point;
            },
            error: function(xhr, status, error) {
                console.error('Error: ' + error);
                alert('Hubo un error al procesar la donación.');
            }
        });
    });
  });