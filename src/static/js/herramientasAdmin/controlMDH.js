document.getElementById('checkStatusButton').addEventListener('click', function() {
    fetch('/herramientasSheet_accionesSheet_actualizaLuz')
        .then(response => response.json())
        .then(data => {
            const statusLight = document.getElementById('statusLight');
            if (data.luzMDH_control) {
                // Si está funcionando, poner verde
                statusLight.style.backgroundColor = '#00ff00'; // Opcional, solo para asegurarse que se cambie directamente
                statusLight.classList.remove('red');
                statusLight.classList.add('green');
            } else {
                // Si no está funcionando, poner rojo
                statusLight.style.backgroundColor = '#ff0000'; // Opcional, solo para asegurarse que se cambie directamente
                statusLight.classList.remove('green');
                statusLight.classList.add('red');
            }
            // Reiniciar el estado a gris después de 3 segundos
            setTimeout(() => {
                statusLight.style.backgroundColor = 'grey';
                statusLight.classList.remove('green', 'red'); // Limpiar clases adicionales
            }, 3000);
        })
        .catch(error => console.error('Error:', error));
});









let contador; // Declarar la variable contador fuera de funciones si es necesario

document.getElementById('checkThreadStatusButton').addEventListener('click', function() {
  clearInterval(contador); // Limpiar intervalo anterior si existe
  verificarYActualizarEstado();
});

function verificarYActualizarEstado() {
  fetch('/herramientasSheet_accionesSheet_actualizaLuz_thread')
      .then(response => response.json())
      .then(data => {
          actualizarEstado_luz_ws(data);
          actualizarEstado(data);
          iniciarContador(parseInt(data.hora), parseInt(data.minuto), parseInt(data.segundo));
      })
      .catch(error => {
          console.error('Error:', error);
          // Manejo de errores aquí
      });
}

function actualizarEstado_luz_ws(data) {
  let luzWebsocketValor = (data.luzWebsocket_control === true) ? 'True' : (data.luzWebsocket_control === false ? 'False' : 'False');
  
  if (localStorage.getItem('luzWebsocket_control') !== null) {
      // Si el atributo ya existe en localStorage, lo modificas con el nuevo valor
      localStorage.setItem('luzWebsocket_control', luzWebsocketValor);
  } else {
      // Si el atributo no existe, lo creas con el valor dado o un valor predeterminado
      localStorage.setItem('luzWebsocket_control', luzWebsocketValor);
  }
}


function actualizarEstado(data) {
  const statusLightThread = document.getElementById('statusLightThread');
  const horaValor = document.getElementById('horaValor');
  const minutoValor = document.getElementById('minutoValor');
  const segundoValor = document.getElementById('segundoValor');

  if (data.luzThread_control) {
      statusLightThread.style.backgroundColor = '#00ff00';
      statusLightThread.classList.remove('red');
      statusLightThread.classList.add('green');
  } else {
      statusLightThread.style.backgroundColor = '#ff0000';
      statusLightThread.classList.remove('green');
      statusLightThread.classList.add('red');
  }

  horaValor.textContent = data.hora;
  minutoValor.textContent = data.minuto;
  segundoValor.textContent = data.segundo;
  const statusLight = document.getElementById('statusLight');
  if (data.luzMDH_control) {
      // Si está funcionando, poner verde
      statusLight.style.backgroundColor = '#00ff00'; // Opcional, solo para asegurarse que se cambie directamente
      statusLight.classList.remove('red');
      statusLight.classList.add('green');
  } else {
      // Si no está funcionando, poner rojo
      statusLight.style.backgroundColor = '#ff0000'; // Opcional, solo para asegurarse que se cambie directamente
      statusLight.classList.remove('green');
      statusLight.classList.add('red');
  }
  setTimeout(() => {
    statusLightThread.style.backgroundColor = 'grey';
    statusLightThread.classList.remove('green', 'red');


    statusLight.style.backgroundColor = 'grey';
    statusLight.classList.remove('green', 'red'); // Limpiar clases adicionales

  }, 3000);
}

function iniciarContador(hora, minuto, segundo) {
  let tiempoTotal = 120;

  contador = setInterval(function() {
      tiempoTotal--;

      let minutosRestantes = Math.floor(tiempoTotal / 60);
      let segundosRestantes = tiempoTotal % 60;

      let tiempoRestante = `${minutosRestantes}:${segundosRestantes.toString().padStart(2, '0')}`;

      document.getElementById('contadorValor').textContent = tiempoRestante;

      if (tiempoTotal <= 0) {
          clearInterval(contador);         
              verificarYActualizarEstado();        
      }
  }, 1000);
}

// Función para detener el contador si es necesario
function detenerContador() {
  clearInterval(contador);
}
