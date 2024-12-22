// Evento para el botón "Maquina"
document.getElementById('btnMaquina').addEventListener('click', function() {
  enviarRespuesta('Maquina'); // Llamar a la función con la respuesta "Maquina"
});

// Evento para el botón "Humano"
document.getElementById('btnHumano').addEventListener('click', function() {
  enviarRespuesta('Humano'); // Llamar a la función con la respuesta "Humano"
});
// Función para enviar la respuesta al servidor
function enviarRespuesta(respuesta) {
  
  var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }
    // Seleccionar el elemento <h4> dentro del contenedor
    const preguntaSeleccionada = document.querySelector('#respuesta-panel');

    // Validar que se haya encontrado el elemento
    if (!preguntaSeleccionada) {
      console.error('No se encontró la pregunta seleccionada.');
      return;
    }

    // Obtener los atributos del elemento <h4>
    const pregunta_respuesta_id = preguntaSeleccionada.getAttribute('data-id');
    const usuarioId = preguntaSeleccionada.getAttribute('data-usuario-id');
    const fechaCreacion = preguntaSeleccionada.getAttribute('data-fecha-creacion');
    const quienResponde = preguntaSeleccionada.getAttribute('data-quien-responde'); // Atributo data-quien-responde
    // Validar que todos los datos estén presentes
    if (!pregunta_respuesta_id || !usuarioId || !fechaCreacion) {
      console.error('Faltan datos de la pregunta seleccionada.');
        if (splash) {
          splash.style.display = 'none'; // Ocultar el splash al terminar
      }
      return;
    }

    // Crear el objeto de datos para enviar al servidor
    const datos = {
      pregunta_respuesta_id: pregunta_respuesta_id,
      usuario_id: usuarioId,
      fecha_creacion: fechaCreacion,
      respuesta: respuesta,
      quienResponde: quienResponde
    };

    // Realizar la llamada AJAX con fetch
    fetch('/turing-triviaTuring-crear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(datos), // Convertimos los datos a JSON
    })
      .then((response) => {
        if (splash) {
          splash.style.display = 'none'; // Ocultar el splash al terminar
      }
        if (!response.ok) {
          throw new Error('Error en la respuesta del servidor');
        }
        return response.json(); // Convertir la respuesta a JSON
      })
      .then((data) => {
       
        const resutaldo_devolver = data.resutaldo_devolver; // Acceder al resultado devuelto por el servidor
        const acierto = data.acierto; // Acceder al resultado devuelto por el servidor
        agregarResultadoTrivia(resutaldo_devolver,acierto);
        // Aquí puedes manejar el resultado devuelto por el servidor, como actualizar la UI
      })
      .catch((error) => {
        if (splash) {
          splash.style.display = 'none'; // Ocultar el splash al terminar
      }
        console.error('Error:', error);
      });
}




function agregarResultadoTrivia(resultado_devolver,acierto) {
  // Seleccionar el elemento del DOM por su ID
  const valor = document.getElementById('resutaldo_triva');
  const resultadoTexto = document.getElementById('resultado_texto'); // Elemento para mostrar el texto "Correcto" o "Incorrecto"
  
  if (valor && resultadoTexto) {
    // Asegúrate de que resultado_devolver es un número
    const resultadoNumerico = parseFloat(resultado_devolver);
    if (!isNaN(resultadoNumerico)) {
        // Calcular el porcentaje restante
        const valorReal = 100 - resultadoNumerico;
        // Actualizar el contenido del elemento
        valor.textContent = `${valorReal}%`;
    } else {
        console.error("resultado_devolver no es un número válido:", resultado_devolver);
    }
    
    // Verificar si el resultado es correcto o incorrecto
    if (acierto==1) {
      // Si el resultado es 100%, es correcto, mostrar en verde
      resultadoTexto.textContent = "Correcto";
      resultadoTexto.style.color = "green";
    } else {
      // Si el resultado no es 100%, es incorrecto, mostrar en rojo
      resultadoTexto.textContent = "Incorrecto";
      resultadoTexto.style.color = "red";
    }
    
    
  } else {
    console.error('Los elementos con los IDs "resutaldo_triva" y "resultado_texto" no se encontraron en el DOM.');
  }
}
