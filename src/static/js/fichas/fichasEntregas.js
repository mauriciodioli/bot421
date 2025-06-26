<<<<<<< HEAD
$(document).ready(function() {
    $('#pagarFichaForm').on('submit', function(event) {
      event.preventDefault(); // Evita el envío tradicional

      // Captura los datos del formulario
      const accessToken = $('#pagar_access_token').val(); // Cambiado para coincidir con el campo correcto
      const pagarFichaId = $('#pagarFichaId').val();
      const layoutOrigen = $('#layoutOrigen').val();

      // Realiza la solicitud AJAX
      $.ajax({
        url: '/fichasToken-fichas-pagar',
        type: 'POST',
        data: {
          access_token: accessToken,
          pagarFichaId: pagarFichaId,
          layoutOrigen: layoutOrigen
        },
        success: function(response) {
          if (response.mensaje) {
            alert(response.mensaje); // Mensaje del servidor
          }

          if (response.fichas) {
            actualizarTabla(response.fichas);
          }

          // Cierra el modal
          $('#pagarFichaModal').modal('hide');
        },
        error: function(xhr, status, error) {
          console.error('Error en la solicitud:', error);
          alert('Ocurrió un error al pagar la ficha.');
        }
      });
    });
  });

  function actualizarTabla(datos) {
    var tabla = document.getElementById('tablaDatos').getElementsByTagName('tbody')[0];
    tabla.innerHTML = ''; // Limpiar tabla si es necesario
    
    datos.forEach(function(ficha) {
      var nuevaFila = tabla.insertRow();
      
      var celdaFicha = nuevaFila.insertCell(0);
    
      var celdaInicial = nuevaFila.insertCell(1);
      var celdaCapitalizacion = nuevaFila.insertCell(2);
      var celdaEstado = nuevaFila.insertCell(3);
      var celdaOperaciones = nuevaFila.insertCell(4);

      celdaFicha.innerHTML = ficha.id;
      celdaInicial.innerHTML = ficha.monto_efectivo;
      celdaCapitalizacion.innerHTML = ficha.interes + "%";
      celdaEstado.innerHTML = ficha.estado;

      celdaOperaciones.innerHTML = `
        <button type="button" class="btn btn-danger mx-2" data-bs-toggle="modal" data-bs-target="#eliminarFichaModal" data-ficha-id="${ficha.id}" onclick="setFichaData(this.getAttribute('data-ficha-id'))" ${ficha.estado === 'ACEPTADO' ? 'disabled' : ''}>Reportar</button>
         `;
    });
  }

  function setFichaData(fichaId, fichaIdFicha) {
    const token = localStorage.getItem('access_token');
    $('#pagarFichaId').val(fichaId);
    $('#pagaridFicha').val(fichaIdFicha);
    $('#pagar_access_token').val(token);
=======
$(document).ready(function() {
    $('#pagarFichaForm').on('submit', function(event) {
      event.preventDefault(); // Evita el envío tradicional

      // Captura los datos del formulario
      const accessToken = $('#pagar_access_token').val(); // Cambiado para coincidir con el campo correcto
      const pagarFichaId = $('#pagarFichaId').val();
      const layoutOrigen = $('#layoutOrigen').val();

      // Realiza la solicitud AJAX
      $.ajax({
        url: '/fichasToken-fichas-pagar',
        type: 'POST',
        data: {
          access_token: accessToken,
          pagarFichaId: pagarFichaId,
          layoutOrigen: layoutOrigen
        },
        success: function(response) {
          if (response.mensaje) {
            alert(response.mensaje); // Mensaje del servidor
          }

          if (response.fichas) {
            actualizarTabla(response.fichas);
          }

          // Cierra el modal
          $('#pagarFichaModal').modal('hide');
        },
        error: function(xhr, status, error) {
          console.error('Error en la solicitud:', error);
          alert('Ocurrió un error al pagar la ficha.');
        }
      });
    });
  });

  function actualizarTabla(datos) {
    var tabla = document.getElementById('tablaDatos').getElementsByTagName('tbody')[0];
    tabla.innerHTML = ''; // Limpiar tabla si es necesario
    
    datos.forEach(function(ficha) {
      var nuevaFila = tabla.insertRow();
      
      var celdaFicha = nuevaFila.insertCell(0);
    
      var celdaInicial = nuevaFila.insertCell(1);
      var celdaCapitalizacion = nuevaFila.insertCell(2);
      var celdaEstado = nuevaFila.insertCell(3);
      var celdaOperaciones = nuevaFila.insertCell(4);

      celdaFicha.innerHTML = ficha.id;
      celdaInicial.innerHTML = ficha.monto_efectivo;
      celdaCapitalizacion.innerHTML = ficha.interes + "%";
      celdaEstado.innerHTML = ficha.estado;

      celdaOperaciones.innerHTML = `
        <button type="button" class="btn btn-danger mx-2" data-bs-toggle="modal" data-bs-target="#eliminarFichaModal" data-ficha-id="${ficha.id}" onclick="setFichaData(this.getAttribute('data-ficha-id'))" ${ficha.estado === 'ACEPTADO' ? 'disabled' : ''}>Reportar</button>
         `;
    });
  }

  function setFichaData(fichaId, fichaIdFicha) {
    const token = localStorage.getItem('access_token');
    $('#pagarFichaId').val(fichaId);
    $('#pagaridFicha').val(fichaIdFicha);
    $('#pagar_access_token').val(token);
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
  }