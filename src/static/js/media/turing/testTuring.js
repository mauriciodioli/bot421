//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
(function inicializarPreguntaID() {
  // Verifica si 'pregunta_id_bucle' no está configurado o está indefinido en localStorage
  if (typeof localStorage.getItem('pregunta_id_bucle') === 'undefined' || localStorage.getItem('pregunta_id_bucle') === null) {
      // Si no está configurado o es indefinido, lo inicializa con el valor 1
      localStorage.setItem('pregunta_id_bucle', '1');
      console.log('Pregunta ID inicializada con valor 1');
  } else {
      console.log('Pregunta ID ya estaba configurada:', localStorage.getItem('pregunta_id_bucle'));
  }
})();




//<!------------------------------------------PANEL IZQUIERDO -------------------------------------------------->
//<!------------------------------------------PANEL IZQUIERDO -------------------------------------------------->
//<!------------------------------------------PANEL IZQUIERDO -------------------------------------------------->
//<!------------------------------------------PANEL IZQUIERDO -------------------------------------------------->


//<!------------------------------------------OBTENER PREGUNTA DESDE DB PARA PANEL AUTOMATICO-------------------------------------------------->
//<!------------------------------------------OBTENER PREGUNTA DESDE DB PARA PANEL AUTOMATICO-------------------------------------------------->
//<!------------------------------------------OBTENER PREGUNTA DESDE DB PARA PANEL AUTOMATICO-------------------------------------------------->
//<!------------------------------------------OBTENER PREGUNTA DESDE DB PARA PANEL AUTOMATICO-------------------------------------------------->


  // Función para hacer la solicitud AJAX y actualizar la lista
  function obtenerPregunta() {
  
    if ( localStorage.getItem('pregunta_id_bucle') === 'undefined' || localStorage.getItem('pregunta_id_bucle') === null) {
      // Si no está configurado o es indefinido, lo inicializa con el valor 1
      localStorage.setItem('pregunta_id_bucle', '1');
    }
    
    id = localStorage.getItem('pregunta_id_bucle');
    $.ajax({
        url: '/turing-testTuring-obtener-id/' + id,
        method: 'GET',
        success: function (data) {
       
          localStorage.setItem('pregunta_id_bucle',data.id);
          agregarPreguntaListaDePreguntas(data.id,data.descripcion, data.fechaCreacion);
          // Llama a la función cuando sea necesario (por ejemplo, después de agregar una nueva pregunta)
          cambiarFondoPregunta();
        },
        error: function () {
            console.error('Error al obtener la pregunta');
        }
    });
}



function agregarPreguntaListaDePreguntas(id, descripcion, fechaCreacion) {
   // Obtener la lista de preguntas
  const lista = $('#preguntas-lista');
  const panelPreguntas = document.getElementById('panel-preguntas');  // Selecciona el contenedor con el scroll
  
  // Verificar si la descripción tiene los signos ¿? al principio y al final
  if (descripcion.startsWith('¿') && descripcion.endsWith('?')) {
    // Eliminar los signos ¿? al principio y al final
    descripcion = descripcion.slice(1, -1);
  }

  // Agregar los signos ¿? al principio y al final
  descripcion = '¿' + descripcion + '?';
            

  // Crear un nuevo elemento de lista con la nueva pregunta
  const nuevaPregunta = $('<li id="descripcion" class="list-group-item"></li>')
  .text(descripcion)
  .attr('data-id', id); // Agregar un atributo data-id con el id
  // Agregar la nueva pregunta al final de la lista
  lista.append(nuevaPregunta);

  // Si la lista tiene más de 50 elementos, eliminar el primero
  if (lista.children().length > 50) {
      lista.children().first().remove();
  }

  // Usar setTimeout para asegurar que el DOM esté actualizado antes de mover el scroll
 // setTimeout(() => {
    panelPreguntas.scrollTop = panelPreguntas.scrollHeight;
//}, 100);  // Ajusta el tiempo si es necesario
}



function cambiarFondoPregunta() {
  const listaPreguntas = $('#preguntas-lista');
  const preguntas = listaPreguntas.children();  // Obtiene todos los elementos <li>
  
  // Verifica si hay al menos 9 preguntas
  if (preguntas.length >= 9) {
      // Eliminar la clase 'fondo-verde-claro' de la pregunta que la tenía previamente
      const preguntaAnterior = listaPreguntas.find('.fondo-verde-claro');
      preguntaAnterior.removeClass('fondo-verde-claro');
      
      // Selecciona el noveno elemento desde abajo
      const novenaPregunta = preguntas.eq(-9);  // -9 para contar desde abajo hacia arriba
      
      // Le agrega la clase para cambiar el fondo
      novenaPregunta.addClass('fondo-verde-claro');
  }
}


//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->

function obtenerRespuesta() {
  // Obtener la lista de preguntas
  const listaPreguntas = document.getElementById("preguntas-lista"); // Asegúrate de que este ID sea correcto
  obtenerIp(function(ipCliente) {
    // Verificar que la lista tenga suficientes elementos
    if (listaPreguntas && listaPreguntas.children.length >= 9) {
        // Calcular la posición 9 desde abajo
      
        const preguntaSeleccionada = listaPreguntas.children[listaPreguntas.children.length - 9];
       
        // Verificar si el elemento en esa posición tiene la estructura esperada
        if (preguntaSeleccionada) {
        
            // Obtener el atributo data-id del <li>
            const preguntaId = preguntaSeleccionada.getAttribute('data-id');

            // Obtener el texto del <li> (y asegurarte de que es la descripción correcta)
            const descripcion = preguntaSeleccionada.textContent.trim();

            // Verificar que los valores necesarios existan
            if (descripcion && preguntaId) {
                // Crear un objeto con los datos a enviar
                const data = {
                    pregunta_id: preguntaId,
                    ip_cliente: ipCliente,  // IP pública obtenida
                    descripcion: descripcion
                };

                // Realizar la solicitud con fetch
                fetch('/turing-testTuring-obtener-respuestas-id', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'  // Especificamos que enviamos JSON
                    },
                    body: JSON.stringify(data)  // Convertimos los datos a JSON
                })
                .then(response => response.json())  // Convertir la respuesta en JSON
                .then(data => {
                    
                 
                    const nombre = data.nombre;
                    const respuesta = data.respuesta_ia;
                    const respuesta_id = data.id;
                    const usuario_id = data.usuario_id;
                    const fechaCreacion = new Date().toLocaleString();              
                    
                    // Suponiendo que la respuesta contiene los datos necesarios
                    agregarRespuestaAPanel(
                        nombre, 
                        respuesta, 
                        respuesta_id, 
                        usuario_id, 
                        fechaCreacion
                    );
                })
                .catch(error => {
                    console.error('Error al obtener la pregunta:', error);
                });
            } else {
                console.error('No se pudo obtener la descripción o el ID de la pregunta.');
            }
        } else {
            console.error('No hay una pregunta válida en la posición 9 desde abajo.');
        }
    } else {
        console.error('La lista de preguntas no contiene suficientes elementos.');
    }
});
}




// Llamar la función cada 5 segundos con el id de la pregunta que quieres obtener
setInterval(function () {
  // Puedes cambiar el id según lo necesites
  const id = Math.floor(Math.random() * 100); // ID de ejemplo
  obtenerPregunta(id);
  obtenerRespuesta(id);
}, 10000);







//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->



// Evento para mostrar el modal cuando se hace clic en el encabezado
document.getElementById("respuestaUltimaPregunta").addEventListener("click", function() { 
  cargarPreguntaEnModalRespuesta();


  // Abre el modal cuando se hace clic en el encabezado
  new bootstrap.Modal(document.getElementById("modalrespuestaUltimaPregunta")).show();
});





document.getElementById("enviarRespuestaBtn").addEventListener("click", function() {
  // Obtener la respuesta del input
  if (splash) {
    splash.style.display = 'block'; // Mostrar el splash
}


  // Llamamos a obtenerIp con un callback para procesar el formulario después de obtener la IP
  obtenerIp(function(ipCliente) {
      // Crear un objeto con los datos del formulario
      const formData = {
          descripcion: document.getElementById("respuestaInput").value,  // Usamos la respuesta obtenida del input
          pregunta_id: document.getElementById("modalPreguntaId").value,
          idioma: 'es',
          valor: 'humano',  // Usamos la respuesta para el campo 'valor'
          estado: 'activo',
          dificultad: 'facil',
          categoria: 'general',
          ip_cliente: ipCliente,  // IP pública obtenida
          respuesta_humano: document.getElementById("respuestaInput").value,
          valor_respuesta_usuario:'no',
          valor_respuesta_turing:'no',
          fecha: new Date().toISOString()  // Fecha actual en formato ISO
      };

      // Realizar la petición AJAX usando fetch
      fetch('/turing-turingRespuestas-crear', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'  // Especificamos que enviamos JSON
          },
          body: JSON.stringify(formData)  // Convertimos los datos del formulario a JSON
      })
      .then(response => response.json())
      .then(data => {
           // Ocultar el splash al terminar
           if (splash) {
            splash.style.display = 'none';
        }
          // Cerrar el modal una vez que la petición sea exitosa
          $('#modalrespuestaUltimaPregunta').modal('hide');  // Usando Bootstrap para cerrar el modal
          const nombre = data.nombre;
          const respuesta = data.respuesta;
          const pregunta_id = data.pregunta_id;
          const usuario_id = data.usuario_id;
          const fechaCreacion = new Date().toLocaleString();  // Si no tienes la fecha, usa la fecha actual
          localStorage.setItem('pregunta_id', data.id);  // Guardamos el ID de la pregunta en localStorage
          // Llamar a la función para agregar la pregunta a la lista
          agregarRespuestaAPanel( nombre,respuesta,pregunta_id,usuario_id,fechaCreacion);
      })
      .catch(error => {
           // Ocultar el splash al terminar
           if (splash) {
            splash.style.display = 'none';
        }
          console.error('Error:', error);
      });
  });
});



function agregarRespuestaAPanel(nombre, respuesta, _id, usuario_id, fechaCreacion) {
  
  // Obtener el contenedor principal donde se cargará la respuesta
  const panelPrincipalRespuesta = $('#respuesta-panel-principal');
  const panelNombrePrincipal = $('#nombre-panel-principal-superior'); // Contenedor para el nombre
  
  respuesta = respuesta || ''; // Asigna una cadena vacía si respuesta es null o undefined
  if (respuesta.startsWith('¿') && respuesta.endsWith('?')) {
      respuesta = respuesta.slice(1, -1); // Eliminar los signos
  }
  




  // Crear el nuevo contenido de respuesta como un `h4` con un `span`
  const nuevaRespuesta = $(`
      <h4 class="fw-bold" id="respuesta-panel">
          <span style="color: #90EE90;">${respuesta}</span>
      </h4>
  `);

  const nombre_post = nombre.slice(0, 7);  // Truncamos el nombre a los primeros 7 caracteres

  // Crear el contenido del nombre
  const nuevoNombre = $(`
     <p class="fw-bold text-center" style="color: #007BFF;">${nombre_post}</p>
  `);

  // Agregar atributos `data-*` para almacenar valores ocultos
  nuevaRespuesta
      .attr('data-id', _id)
      .attr('data-usuario-id', usuario_id)
      .attr('data-fecha-creacion', fechaCreacion);

  // Vaciar el contenedor y agregar la nueva respuesta
  panelPrincipalRespuesta.empty().append(nuevaRespuesta);

  // Vaciar el contenedor del nombre y cargar el nuevo nombre
  panelNombrePrincipal.empty().append(nuevoNombre);
}









// Obtener el botón que abre el modal
document.getElementById('btnAbrirModalLastAnswer').addEventListener('click', function() {
    // Mostrar el modal LasAnswersModal usando Bootstrap JS
    var LasAnswersModal = new bootstrap.Modal(document.getElementById('LasAnswersModal'));
    LasAnswersModal.show();
  });
  
 
 
 
 
 
 


//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
// Función para reiniciar el temporizador
let tiempoRestante = 17;  // 2 minutos en segundos 120
let timerElement = document.getElementById("timer");
// Iniciar el temporizador cada segundo

  /**
   * Reinicia el temporizador para que vuelva a contar desde 2 minutos.
   * Se utiliza para restablecer el temporizador después de enviar una respuesta.
   */
function reiniciarTemporizador() {

  // Resetear el tiempo y actualizar la visualización
  tiempoRestante = 17;
 // actualizarTemporizador(tiempoRestante,timerElement);
}

// Función para actualizar el temporizador
function actualizarTemporizador(tiempoRestante,timerElement) {
    let minutos = Math.floor(tiempoRestante / 60);
    let segundos = tiempoRestante % 60;

    // Formatear el tiempo a "mm:ss"
    let tiempoFormateado = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
    timerElement.textContent = tiempoFormateado;

    // Decrementar el tiempo
    if (tiempoRestante > 0) {
        tiempoRestante--;
    } else {
        // Cerrar el modal cuando el tiempo llegue a cero
        $('#modalrespuestaUltimaPregunta').modal('hide');
        
        // Asegurarse de que el fondo oscuro desaparezca
        $('.modal-backdrop').remove();  // Eliminar el fondo oscuro manualmente
        
        // Restaurar el enfoque a la página principal
        document.body.focus();
    }
}



// Función que se activa cuando el modal es abierto
document.getElementById("respuestaUltimaPregunta").addEventListener("click", function() {
    // Mostrar el modal
    new bootstrap.Modal(document.getElementById("modalrespuestaUltimaPregunta")).show();
});




// Función para cargar la pregunta en el modal de la posición 9 desde abajo
function cargarPreguntaEnModalRespuesta() {
  // Obtener la lista de preguntas
  const listaPreguntas = document.getElementById("preguntas-lista"); // Suponiendo que este es el ID de la lista de preguntas

  // Verificar si hay al menos 9 preguntas
  if (listaPreguntas.children.length < 9) {
    console.error("No hay suficientes preguntas");
    return; // Si no hay suficientes preguntas, salir de la función
  }

  // Calcular la posición 9 desde abajo
  const preguntaSeleccionada = listaPreguntas.children[listaPreguntas.children.length - 9];

  // Verificar si la pregunta existe en esa posición
  if (preguntaSeleccionada) {
      // Obtener la descripción de la pregunta
      const descripcion = preguntaSeleccionada.querySelector(".descripcion")?.textContent || 'Descripción no disponible'; // Asegúrate de que exista la clase
      const preguntaId = preguntaSeleccionada.querySelector(".data-id")?.textContent || 'ID no disponible'; // Asegúrate de que exista la clase

      // Cargar los datos en el modal
      document.getElementById("modalDescripcion").textContent = descripcion; // "descripcion";
      document.getElementById("modalPreguntaId").value = preguntaId; // "7";  // Usamos `value` para un input
  }
}









//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO -------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->
//<!------------------------------------------PREGUNTAR DESDE USUARIO PANEL DERECHO-------------------------------------------------->

document.getElementById("preguntar").addEventListener("click", function() {
  // Abre el modal cuando se hace clic en el encabezado
  new bootstrap.Modal(document.getElementById("preguntaModal")).show();
});
 // Cuando se hace clic en el botón "Enviar"
 document.getElementById('enviarPreguntaBtn').onclick = function() {

  var splash = document.querySelector('.splashCarga');
    if (splash) {
        splash.style.display = 'block'; // Mostrar el splash
    }

  // Llamamos a obtenerIp con un callback para procesar el formulario después de obtener la IP
  obtenerIp(function(ipCliente) {
    // Crear un objeto con los datos del formulario
    const formData = {
      descripcion: document.getElementById('preguntaInput').value,
      idioma: 'es',
      valor: document.getElementById('preguntaInput').value,  // Usamos el valor de la pregunta para el campo 'valor'
      estado: 'activo',
      dificultad: 'facil',
      categoria: 'general',
      ip_cliente: ipCliente,  // IP pública obtenida
      respuesta_ia: 'no respondido',
      fecha: new Date().toISOString()  // Fecha actual en formato ISO
    };

    // Realizar la petición AJAX usando fetch
    fetch('/turing-testTuring-crear', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'  // Especificamos que enviamos JSON
      },
      body: JSON.stringify(formData)  // Convertimos los datos del formulario a JSON
    })
    .then(response => response.json())
    .then(data => {
        
          if (splash) {
            splash.style.display = 'none'; // Ocultar el splash al terminar
        }
        // Cerrar el modal una vez que la petición sea exitosa
        $('#preguntaModal').modal('hide');  // Usando Bootstrap para cerrar el modal
        const nombre = data.nombre;
        const descripcion = data.descripcion;
        const fechaCreacion = new Date().toLocaleString();  // Si no tienes la fecha, usa la fecha actual
        localStorage.setItem('pregunta_id',data.id);
        // Llamar a la función para agregar la pregunta a la lista
        agregarPreguntaLista(nombre, descripcion, fechaCreacion);
        
    })
    .catch(error => {
      if (splash) {
        splash.style.display = 'none';
    }
      console.error('Error:', error);
    });
  });
};



// Función para agregar la pregunta a la lista
function agregarPreguntaLista(nombre, descripcion, fechaCreacion) {
  const lista = document.getElementById('chat-lista');
  const panelChat = document.getElementById('panel-chat');  // Selecciona el contenedor con el scroll
  
  // Crear un nuevo elemento de lista
  const nuevoItem = document.createElement('li');
  nuevoItem.classList.add('list-group-item', 'd-flex', 'align-items-center');
  
  // Extraer la parte antes del guion bajo del nombre (números)
  const avatarText = nombre.split('_')[0];  // Obtiene la primera parte del nombre antes del guion bajo
  localStorage.setItem('avatarText', avatarText);
  
  const nombre_post = nombre.slice(0, 7);  // Truncamos el nombre a los primeros 7 caracteres

  // Verificar si la descripción tiene los signos ¿? al principio y al final
  if (descripcion.startsWith('¿') && descripcion.endsWith('?')) {
    // Eliminar los signos ¿? al principio y al final
    descripcion = descripcion.slice(1, -1);
  }

  // Agregar los signos ¿? al principio y al final
  descripcion = '¿' + descripcion + '?';


  // Crear el contenido del nuevo elemento
  const contenido = `
      <div class="rounded-circle me-2" style="width: 40px; height: 40px; display: flex; justify-content: center; align-items: center; background-color: #ddd; font-size: 18px; color: #fff;">
          ${avatarText}  <!-- Aquí mostramos los primeros números del nombre -->
      </div>
      <div>
          <span><strong>${nombre_post}:</strong> ${descripcion}</span><br>
          <span><strong>Fecha:</strong> ${fechaCreacion}</span><br>
      </div>
  `;
  
  nuevoItem.innerHTML = contenido;

  // Agregar el nuevo item al final de la lista
  lista.appendChild(nuevoItem);

  // Si la lista tiene más de 50 elementos, eliminar el primero
  if (lista.children.length > 50) {
      lista.removeChild(lista.firstChild);
  }

  // Desplazar el scroll hacia abajo para que la última pregunta siempre sea visible
  panelChat.scrollTop = panelChat.scrollHeight;

}
















function obtenerIp(callback) {
  fetch('https://api.ipify.org?format=json')
      .then(response => response.json())
      .then(data => {
          callback(data.ip);  // Pasamos la IP a la función callback
      })
      .catch(error => {
          console.error('Error al obtener la IP:', error);
          callback('0.0.0.0');  // Valor por defecto si hay un error
      });
}




