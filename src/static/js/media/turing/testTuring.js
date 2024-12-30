//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
//<!------------------------------------------AQUI SE INICIALIZA EL ID DE LA PREGUNTA -------------------------------------------------->
(function inicializarPreguntaID() {
  // Verifica si 'pregunta_id_bucle' no está configurado o está indefinido en localStorage
  if (typeof localStorage.getItem('pregunta_id_bucle') === 'undefined' || localStorage.getItem('pregunta_id_bucle') === null) {
      // Si no está configurado o es indefinido, lo inicializa con el valor 1
      localStorage.setItem('pregunta_id_bucle', '1');
   
  } else {
      console.log('Pregunta ID ya estaba configurada:', localStorage.getItem('pregunta_id_bucle'));
  }
  

  if (typeof localStorage.getItem('usuario_id_chat') === 'undefined' || localStorage.getItem('usuario_id_chat') === null) {
    // Si no está configurado o es indefinido, lo inicializa con el valor 1
    localStorage.setItem('usuario_id_chat', '1');
   
} else {
    console.log('Pregunta ID ya estaba configurada:', localStorage.getItem('usuario_id_chat'));
}


if (typeof localStorage.getItem('selectedModel') === 'undefined' || localStorage.getItem('selectedModel') === null) {
  // Si no está configurado o es indefinido, lo inicializa con el valor 1
  localStorage.setItem('selectedModel', 'gpt2Model');
 
} else {
  console.log('Pregunta ID ya estaba configurada:', localStorage.getItem('selectedModel'));
}


if (typeof localStorage.getItem('activado_voz') === 'undefined' || localStorage.getItem('activado_voz') === null) {
  // Si no está configurado o es indefinido, lo inicializa con el valor 1
  localStorage.setItem('activado_voz', 'false');
  console.log('activado_voz false');
} else {
  console.log('activado_voz:', localStorage.getItem('activado_voz'));
}


if (typeof localStorage.getItem('idioma_es') === 'undefined' || localStorage.getItem('idioma_es') === null) {
  // Si no está configurado o es indefinido, lo inicializa con el valor 1
  localStorage.setItem('idioma_es', 'false');
  console.log('idioma_es false');
} else {
  console.log('idioma_es:', localStorage.getItem('idioma_es'));
}


if (typeof localStorage.getItem('seleccionCategoria') === 'undefined' || localStorage.getItem('seleccionCategoria') === null) {
  // Si no está configurado o es indefinido, lo inicializa con el valor 1
  localStorage.setItem('seleccionCategoria', 'general');
  console.log('seleccionCategoria general');
} else {
  console.log('seleccionCategoria:', localStorage.getItem('seleccionCategoria'));
}


if (typeof localStorage.getItem('tiempoLecturaBuclePreguntas') === 'undefined' || localStorage.getItem('tiempoLecturaBuclePreguntas') === null) {
  // Si no está configurado o es indefinido, lo inicializa con el valor 1
  localStorage.setItem('tiempoLecturaBuclePreguntas', '40000');
  console.log('tiempoLecturaBuclePreguntas 40000');
} else {
  console.log('tiempoLecturaBuclePreguntas:', localStorage.getItem('tiempoLecturaBuclePreguntas'));
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
    // Verifica y establece valores predeterminados en localStorage
    if (!localStorage.getItem('pregunta_id_bucle')) {
      localStorage.setItem('pregunta_id_bucle', '1');
  }
  if (!localStorage.getItem('seleccionCategoria')) {
      localStorage.setItem('seleccionCategoria', 'general');
  }

      // Obtiene los valores del localStorage con valores predeterminados
      const id = localStorage.getItem('pregunta_id_bucle') || 1; // ID predeterminado en caso de que sea null
      const categoria = localStorage.getItem('seleccionCategoria') || 'general'; // Categoría predeterminada
      // Realiza la solicitud AJAX con jQuery
      $.ajax({
          url: '/turing-testTuring-obtener-id/' + id + '/categoria/' + categoria, // Endpoint con parámetros
          method: 'GET', // Método HTTP
      success: function (data) {
          // Actualiza localStorage con el nuevo ID de pregunta
          localStorage.setItem('pregunta_id_bucle', data.id);

          // Actualiza la interfaz con la nueva pregunta
          agregarPreguntaListaDePreguntas(data.id, data.descripcion, data.idioma, data.fechaCreacion, data.categoria);
          cambiarFondoPregunta(data.descripcion);
      },
      error: function (xhr, status, error) {
          console.error('Error al obtener la pregunta:', error);
      }
  });
}





function agregarPreguntaListaDePreguntas(id, descripcion,idioma, fechaCreacion, categoria) {
   // Obtener la lista de preguntas
  categoria_guardada=localStorage.getItem('seleccionCategoria');

  
    // Verificar si la categoría de la pregunta coincide con la seleccionada o si no es privada
    if (categoria_guardada === 'pregunta-Privada' && categoria !== 'pregunta-Privada') {
      // Si la categoría seleccionada es "Privada", no mostrar otras categorías.
      return;
  }

  if (categoria_guardada !== 'pregunta-Privada' && categoria === 'pregunta-Privada') {
      // Si la categoría seleccionada no es "Privada", no mostrar preguntas privadas.
      return;
  }
    
  
      const lista = $('#preguntas-lista');
      const panelPreguntas = document.getElementById('panel-preguntas');  // Selecciona el contenedor con el scroll
      
      if(idioma=='es'){        
              
          // Verificar si la descripción tiene los signos ¿? al principio y al final
          if (descripcion.startsWith('¿') && descripcion.endsWith('?')) {
          // Eliminar los signos ¿? al principio y al final
          descripcion = descripcion.slice(1, -1);
          }

          // Agregar los signos ¿? al principio y al final
          descripcion = '¿' + descripcion + '?';
      }else{

            // Verificar si la descripción tiene los signos ¿? al principio y al final

            if ( descripcion.endsWith('?')) {
            // Eliminar los signos ¿? al principio y al final
            descripcion = descripcion.slice(0, -1);
            }

            // Agregar los signos ¿? al al final
            descripcion = descripcion + '?';
      }

                

      // Crear un nuevo elemento de lista con la nueva pregunta
      const nuevaPregunta = $('<li id="descripcion" class="list-group-item"></li>')
      .text(descripcion)
      .addClass('list-group-item pregunta-item') // Clase 'pregunta-item' añadida
      .attr('data-id', id); // Agregar un atributo data-id con el id




       // Verificar si la función mostrarMenu está definida antes de asignar el evento
        if (typeof mostrarMenu === 'function') {
          nuevaPregunta.on('click', function () {
              mostrarMenu({
                  target: this // Pasar el elemento clicado como el target del evento
              });
          });
      } else {
          console.error('mostrarMenu no está definida.');
      }



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



function cambiarFondoPregunta(descripcion) {
  const listaPreguntas = $('#preguntas-lista');
  const preguntas = listaPreguntas.children();  // Obtiene todos los elementos <li>
  
  // Verifica si hay al menos 6 preguntas
  if (preguntas.length >= 6) {
      // Eliminar la clase 'fondo-verde-claro' de la pregunta que la tenía previamente
      const preguntaAnterior = listaPreguntas.find('.fondo-verde-claro');
      preguntaAnterior.removeClass('fondo-verde-claro');
      
      // Selecciona el noveno elemento desde abajo
      const novenaPregunta = preguntas.eq(-6);  // -6 para contar desde abajo hacia arriba
//console.log(novenaPregunta);
      // Le agrega la clase para cambiar el fondo
      novenaPregunta.addClass('fondo-verde-claro');
  
      enviarRespuestaDeVoz(novenaPregunta.text());
      setTimeout(() => {
        // Código que deseas ejecutar después del delay
        console.log("Ejecutando después del retraso");
      }, 500); // Ajusta el tiempo del retraso (en milisegundos)
  
 }
  
}


//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->
//<!------------------------------------------OBTENER RESPUESTA DESDE DB AUTOMATICA IA-------------------------------------------------->

/**
 * Verifica si la bandera de activación de la IA está desactivada.
 * @returns {boolean} `true` si la bandera está desactivada, `false` en caso contrario.
 */function obtenerBanderaActivado() {
  
  // Verificar si existe la clave 'bandera_activado' en localStorage
  if (localStorage.getItem('model_activado')) {
    // Si existe, devolver su valor
    return localStorage.getItem('model_activado');
  } else {
    // Si no existe, devolver false
    return false;
  }
}

function obtenerRespuesta() {
  // Obtener la lista de preguntas
  const listaPreguntas = document.getElementById("preguntas-lista"); // Asegúrate de que este ID sea correcto
  obtenerIp(function(ipCliente) {
    // Verificar que la lista tenga suficientes elementos

    if (listaPreguntas && listaPreguntas.children.length >= 6) {
        // Calcular la posición 9 desde abajo
        
        const preguntaSeleccionada = listaPreguntas.children[listaPreguntas.children.length - 6];
       
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
                    descripcion: descripcion,
                    boton_modelo_activado: obtenerBanderaActivado(),
                    selectedModel: localStorage.getItem('selectedModel')
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
                    const quienResponde = data.quienResponde;            
                    
                    // Suponiendo que la respuesta contiene los datos necesarios
                    agregarRespuestaAPanel(
                        nombre, 
                        respuesta, 
                        respuesta_id, 
                        usuario_id, 
                        fechaCreacion,
                        quienResponde
                    );
                })
                .catch(error => {
                    console.error('Error al obtener la pregunta:', error);
                });
            } else {
                console.error('No se pudo obtener la descripción o el ID de la pregunta.');
            }
          } else {
             console.error('No hay una pregunta válida en la posición 6 desde abajo.');
        }
    } else {
        console.error('La lista de preguntas no contiene suficientes elementos.');
    }
});
}







// Declarar variables globales
let tiempoLectura = parseInt(localStorage.getItem('tiempoLecturaBuclePreguntas')) || 40000; // Valor inicial
let intervalo; // Guardará el ID del setInterval

// Función para iniciar el bucle
function iniciarIntervalo() {
  if (intervalo) {
    clearInterval(intervalo); // Detener cualquier intervalo previo
  }

  // Crear un nuevo intervalo con el tiempo actual
  intervalo = setInterval(function () {
    const id = Math.floor(Math.random() * 100); // Genera un ID aleatorio

    // Llama a las funciones necesarias
    obtenerChatUsuariosPregunta();
    obtenerPregunta(id);
    obtenerRespuesta(id);
  }, tiempoLectura);

  // Actualiza el valor mostrado
  document.getElementById('tiempoLecturaActual').textContent = `Tiempo de lectura: ${tiempoLectura} ms`;
}

// Función para actualizar dinámicamente el tiempo de lectura
function actualizarTiempoLectura(nuevoTiempo) {
  tiempoLectura = nuevoTiempo; // Actualizar la variable
  localStorage.setItem('tiempoLecturaBuclePreguntas', nuevoTiempo); // Guardar en localStorage
  iniciarIntervalo(); // Reiniciar el intervalo con el nuevo tiempo
}

// Iniciar el intervalo por primera vez
iniciarIntervalo();

// Ejemplo: Incrementar el tiempo
document.getElementById('incrementarTiempo').addEventListener('click', function () {
  actualizarTiempoLectura(tiempoLectura + 5000); // Incrementar 5 segundos
});

// Ejemplo: Reducir el tiempo
document.getElementById('decrementarTiempo').addEventListener('click', function () {
  actualizarTiempoLectura(Math.max(tiempoLectura - 5000, 1000)); // Reducir 5 segundos, mínimo 1 segundo
});








document.addEventListener('DOMContentLoaded', function () {
  // Inicializa tiempoLectura desde localStorage o usa un valor por defecto
  let tiempoLectura = parseInt(localStorage.getItem('tiempoLecturaBuclePreguntas'), 10) || 40000;

  // Actualiza el valor mostrado en pantalla
  const actualizarTextoTiempo = () => {
    document.getElementById('tiempoLecturaActual').textContent = `Tiempo de lectura: ${tiempoLectura} ms`;
  };

  actualizarTextoTiempo(); // Muestra el valor inicial

  // Incrementar tiempo
  document.getElementById('incrementarTiempo').addEventListener('click', () => {
    tiempoLectura += 1000; // Incrementa en 1000 ms
    localStorage.setItem('tiempoLecturaBuclePreguntas', tiempoLectura); // Actualiza localStorage
    actualizarTextoTiempo();
  });

  // Decrementar tiempo
  document.getElementById('decrementarTiempo').addEventListener('click', () => {
    if (tiempoLectura > 1000) { // Evita tiempos menores a 1000 ms
      tiempoLectura -= 1000; // Decrementa en 1000 ms
      localStorage.setItem('tiempoLecturaBuclePreguntas', tiempoLectura); // Actualiza localStorage
      actualizarTextoTiempo();
    }
  });
});






//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->
//<!------------------------------------------ENVIAR RESPUESTA DE USUARIO-------------------------------------------------->



// Evento para mostrar el modal cuando se hace clic en el encabezado
document.getElementById("respuestaUltimaPregunta").addEventListener("click", function() { 
  cargarPreguntaEnModalRespuesta();
  // Abre el modal cuando se hace clic en el encabezado
  new bootstrap.Modal(document.getElementById("modalrespuestaUltimaPregunta")).show();
  abrirModalConTemporizador();
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
        document.getElementById("respuestaInput").value='';
          // Cerrar el modal una vez que la petición sea exitosa
          $('#modalrespuestaUltimaPregunta').modal('hide');  // Usando Bootstrap para cerrar el modal
          const nombre = data.nombre;
          const respuesta = data.respuesta;
          const pregunta_id = data.pregunta_id;
          const usuario_id = data.usuario_id;
          const fechaCreacion = new Date().toLocaleString();  // Si no tienes la fecha, usa la fecha actual
          localStorage.setItem('pregunta_id', data.id);  // Guardamos el ID de la pregunta en localStorage
          // Llamar a la función para agregar la pregunta a la lista
          agregarRespuestaAPanel( nombre,respuesta,pregunta_id,usuario_id,fechaCreacion,'respondidoPorUsuario');
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



function agregarRespuestaAPanel(nombre, respuesta, _id, usuario_id, fechaCreacion,quienResponde) {
  
  // Obtener el contenedor principal donde se cargará la respuesta
  const panelPrincipalRespuesta = $('#respuesta-panel-principal');
  const panelNombrePrincipal = $('#nombre-panel-principal-superior'); // Contenedor para el nombre
  


  respuesta = respuesta || ''; // Asigna una cadena vacía si respuesta es null o undefined
  respuesta = String(respuesta); // Asegúrate de que sea una cadena
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
      .attr('data-fecha-creacion', fechaCreacion)
      .attr('data-quien-responde',quienResponde);

      // Cargar los valores en el panel de respuestas
  //$('#nombre-respuesta').text(`ID: ${_id}`);
  //$('#respuesta-panel-principal').text(`Usuario ID: ${usuario_id}`);
  //$('#atributos-respuesta').html(`
  //    <p>Fecha de Creación: ${fechaCreacion}</p>
  //    <p>Quién Responde: ${quienResponde}</p>
  //`);
  // Vaciar el contenedor y agregar la nueva respuesta
  panelPrincipalRespuesta.empty().append(nuevaRespuesta);

  // Vaciar el contenedor del nombre y cargar el nuevo nombre
  panelNombrePrincipal.empty().append(nuevoNombre);

  enviarRespuestaDeVoz(respuesta);
  
}



function enviarRespuestaDeVoz(respuesta) {
  

var activado_voz = localStorage.getItem('activado_voz');
var idioma_es = localStorage.getItem('idioma_es');

  if (!window.speechSynthesis) {
      console.error('La síntesis de voz no está soportada en este navegador.');
      return;
  }

  if (activado_voz === 'true' && respuesta.trim() !== '') {
      const speech = new SpeechSynthesisUtterance(respuesta);
      speech.lang = idioma_es === 'true' ? 'es-ES' : 'en-US';
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(speech);
  }

}




 
 
 
 
 
 


//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->
//<!------------------------------------------TAREAS MODAL ENVIAR RESPUESTA-------------------------------------------------->

/**
 * Función para abrir el modal con un temporizador y mostrar la pregunta y respuesta
 * correspondientes cada 10 segundos. El temporizador dura 2 minutos.
 */
function abrirModalConTemporizador() {
  // Variables locales
  const DURACION_MODAL = 120; // Duración en segundos (2 minutos)
  let tiempoRestante = DURACION_MODAL;
  let temporizador; // ID del intervalo del temporizador
  let intervaloPreguntas; // ID del intervalo de preguntas

  // Mostrar el modal
  const modal = new bootstrap.Modal(document.getElementById('modalrespuestaUltimaPregunta'));
  modal.show();

  // Elemento del temporizador en el modal
  const timerElement = document.getElementById('timer');

  // Función para actualizar el temporizador
  function actualizarTemporizador() {
      const minutos = Math.floor(tiempoRestante / 60);
      const segundos = tiempoRestante % 60;

      // Formatear el tiempo a "mm:ss"
      const tiempoFormateado = `${minutos.toString().padStart(2, '0')}:${segundos.toString().padStart(2, '0')}`;
      timerElement.textContent = tiempoFormateado;

      if (tiempoRestante > 0) {
          tiempoRestante--;
      } else {
          // Detener el temporizador y cerrar el modal cuando el tiempo llegue a cero
          clearInterval(temporizador);
          clearInterval(intervaloPreguntas);
          cerrarModal();
      }
  }

  // Función para cerrar el modal
  function cerrarModal() {
      modal.hide();

      // Asegurarse de eliminar cualquier fondo oscuro sobrante
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());

      // Restaurar el enfoque a la página principal
      document.body.classList.remove('modal-open'); // Quitar la clase que deshabilita el scroll
      document.body.style.overflow = ''; // Restaurar el scroll si fue deshabilitado
      document.body.focus();

      // Detener intervalos en caso de que no hayan sido limpiados
      clearInterval(temporizador);
      clearInterval(intervaloPreguntas);
  }

  // Iniciar el temporizador (se ejecuta cada segundo)
  temporizador = setInterval(actualizarTemporizador, 1000);

  // Iniciar el intervalo para obtener preguntas y respuestas
  intervaloPreguntas = setInterval(() => {
      const id = Math.floor(Math.random() * 100); // Generar ID aleatorio
      obtenerPregunta(id);
      obtenerRespuesta(id);
  }, 10000); // Cada 10 segundos

  // Al cerrar el modal manualmente, detener ambos intervalos y limpiar el fondo
  document.getElementById('modalrespuestaUltimaPregunta').addEventListener('hidden.bs.modal', () => {
      cerrarModal();
  });
}












// Función para cargar la pregunta en el modal de la posición 9 desde abajo
function cargarPreguntaEnModalRespuesta() {
  // Obtener la lista de preguntas
  const listaPreguntas = document.getElementById("preguntas-lista"); // Suponiendo que este es el ID de la lista de preguntas

  // Verificar si hay al menos 6 preguntas
  if (listaPreguntas.children.length < 6) {
    console.error("No hay suficientes preguntas");
    return; // Si no hay suficientes preguntas, salir de la función
  }

  // Calcular la posición 7 desde abajo
  const preguntaSeleccionada = listaPreguntas.children[listaPreguntas.children.length - 6];
  console.log(preguntaSeleccionada);

  // Verificar si la pregunta existe en esa posición
  if (preguntaSeleccionada) {
      // Obtener la descripción de la pregunta directamente del texto del <li>
      const descripcion = preguntaSeleccionada.textContent.trim(); // Eliminar espacios innecesarios

      // Obtener el ID desde el atributo data-id
      const preguntaId = preguntaSeleccionada.getAttribute("data-id");

      // Cargar los datos en el modal
      document.getElementById("modalDescripcion").textContent = descripcion; // Establecer la descripción en el modal
      document.getElementById("modalPreguntaId").value = preguntaId; // Establecer el ID en el input
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
document.getElementById("preguntar").addEventListener("click", function () {
  // Abre el modal cuando se hace clic en el encabezado
  new bootstrap.Modal(document.getElementById("preguntaModal")).show();

  // Seleccionar elementos
  const checkbox = document.getElementById('mostrarRespuestaCheckbox');
  const respuestaInput = document.getElementById('respuestaInputForUserChat');

  // Verificar que los elementos existen
  if (checkbox && respuestaInput) {
      // Remover cualquier listener previo para evitar duplicados
      checkbox.removeEventListener('change', toggleRespuestaInput);

      // Agregar evento al checkbox
      checkbox.addEventListener('change', toggleRespuestaInput);

      // Función para manejar el cambio del checkbox
      function toggleRespuestaInput() {
          if (this.checked) {
              respuestaInput.style.display = 'block'; // Mostrar el input
          } else {
              respuestaInput.style.display = 'none'; // Ocultar el input
          }
      }
  }

  document.getElementById('mostrarCategoriasCheckbox').addEventListener('change', function () {
    const categoriaSelect = document.getElementById('categoriaSelectForUserChat');
    if (this.checked) {
      categoriaSelect.style.display = 'block'; // Mostrar selección de categorías
    } else {
      categoriaSelect.style.display = 'none'; // Ocultar selección de categorías
    }
  });
  


});
// Cuando se hace clic en el botón "Enviar"
document.getElementById('enviarPreguntaBtn').onclick = function() {
  var splash = document.querySelector('.splashCarga');
  if (splash) {
    splash.style.display = 'block'; // Mostrar el splash
  }

  // Llamamos a obtenerIp con un callback para procesar el formulario después de obtener la IP
  obtenerIp(function(ipCliente) {
    // Obtener los valores del formulario
    const pregunta = document.getElementById('preguntaInput').value;
    const respuesta = document.getElementById('respuestaInputForUserChat').value;
    // Obtener referencia al checkbox
    const seleccionarIdiomaCheckbox = document.getElementById("seleccionarIdiomaCheckbox");

    // Declarar la variable idioma
    let idioma;
    // Función para actualizar el valor de la variable según el estado del checkbox
    function actualizarIdioma() {
      if (seleccionarIdiomaCheckbox.checked) {
        idioma = 'es';
        console.log("Idioma español seleccionado");
      } else {
        idioma = 'in';
        console.log("Idioma español desmarcado");
      }
      // Mostrar el valor actual de la variable
      console.log("Idioma actual:", idioma);
    }

    // Detectar cambios en el checkbox
    seleccionarIdiomaCheckbox.addEventListener("change", actualizarIdioma);

    // Establecer el valor inicial al cargar la página
    actualizarIdioma();




    
    // Detectar categoría
    const categoriaSelect = document.getElementById('categoriaSelectForUserChat');
    const categoriaSeleccionada = categoriaSelect.value || 'Libre'; // Si no hay selección, usa 'libre'

    // Crear un objeto con los datos del formulario
    const formData = {
      descripcion: pregunta,
      idioma: idioma,
      valor: pregunta,  // Usamos el valor de la pregunta para el campo 'valor'
      estado: 'activo',
      dificultad: 'facil',
      categoria: categoriaSeleccionada,
      ip_cliente: ipCliente,  // IP pública obtenida
      respuesta_ia: respuesta.trim() !== '' ? respuesta : 'no respondido', // Verifica si la respuesta está vacía
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
        // Limpiar el contenido del input antes de cerrar el modal
        document.getElementById('preguntaInput').value = '';  // Limpiar el input
        document.getElementById('respuestaInputForUserChat').value='';
        // Cerrar el modal una vez que la petición sea exitosa
        $('#preguntaModal').modal('hide');  // Usando Bootstrap para cerrar el modal
        const nombre = data.nombre;
        const idioma = data.idioma;
        const descripcion = data.descripcion;
        const fechaCreacion = new Date().toLocaleString();  // Si no tienes la fecha, usa la fecha actual
        localStorage.setItem('pregunta_id',data.id);
        // Llamar a la función para agregar la pregunta a la lista
       
        agregarPreguntaLista(nombre, descripcion, idioma, fechaCreacion);
        
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
function agregarPreguntaLista(nombre, descripcion,idioma, fechaCreacion) {
  const lista = document.getElementById('chat-lista');
  const panelChat = document.getElementById('panel-chat');  // Selecciona el contenedor con el scroll
  
  // Crear un nuevo elemento de lista
  const nuevoItem = document.createElement('li');
  nuevoItem.classList.add('list-group-item', 'd-flex', 'align-items-center');
  
  // Extraer la parte antes del guion bajo del nombre (números)
  const avatarText = nombre.split('_')[0];  // Obtiene la primera parte del nombre antes del guion bajo
  localStorage.setItem('avatarText', avatarText);
  
  const nombre_post = nombre.slice(0, 7);  // Truncamos el nombre a los primeros 7 caracteres
  
        if(idioma=='es'){        
          
            // Verificar si la descripción tiene los signos ¿? al principio y al final
            if (descripcion.startsWith('¿') && descripcion.endsWith('?')) {
            // Eliminar los signos ¿? al principio y al final
            descripcion = descripcion.slice(1, -1);
            }

            // Agregar los signos ¿? al principio y al final
            descripcion = '¿' + descripcion + '?';
        }else{

              // Verificar si la descripción tiene los signos ¿? al principio y al final

              if ( descripcion.endsWith('?')) {
              // Eliminar los signos ¿? al principio y al final
              descripcion = descripcion.slice(0, -1);
              }

              // Agregar los signos ¿? al al final
              descripcion = descripcion + '?';
        }


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


































document.addEventListener('DOMContentLoaded', function() {
  // Elementos de los modelos
  const conectarButton = document.getElementById('conectar');
  const gpt2Model = document.getElementById('gpt2Model');
  const bertModel = document.getElementById('bertModel');
  const distilbertModel = document.getElementById('distilbertModel');

  // Obtener modelo seleccionado desde localStorage
  let selectedModel = localStorage.getItem('selectedModel') || 'gpt2Model'; // Modelo por defecto

  // Actualizar selección al cargar
  function updateSelectedModelUI() {
    if (selectedModel === 'gpt2Model') {
      gpt2Model.classList.add('active');
    } else if (selectedModel === 'bertModel') {
      bertModel.classList.add('active');
    } else if (selectedModel === 'distilbertModel') {
      distilbertModel.classList.add('active');
    }
  }

  // Guardar modelo seleccionado
  function saveSelectedModel(model) {
    selectedModel = model;
    localStorage.setItem('selectedModel', model);

    // Resetear clases activas
    gpt2Model.classList.remove('active');
    bertModel.classList.remove('active');
    distilbertModel.classList.remove('active');

    // Activar modelo seleccionado
    updateSelectedModelUI();
  }

  // Configurar eventos para cada modelo
  if (gpt2Model) {
    gpt2Model.addEventListener('click', () => saveSelectedModel('gpt2Model'));
  }
  if (bertModel) {
    bertModel.addEventListener('click', () => saveSelectedModel('bertModel'));
  }
  if (distilbertModel) {
    distilbertModel.addEventListener('click', () => saveSelectedModel('distilbertModel'));
  }

  // Inicializar UI
  updateSelectedModelUI();


  






  if (conectarButton) {
    // Verificar si ya existe el valor en localStorage
    let modelActivado = localStorage.getItem('model_activado');

    // Si no existe, activarlo por defecto
    if (modelActivado === null) {
      modelActivado = true; // Se establece como activado
      localStorage.setItem('model_activado', modelActivado);
    } else {
      // Convertir el valor a booleano
      modelActivado = JSON.parse(modelActivado);
    }

    // Función para alternar el estado
    function toggleModelState() {
      // Alternar el estado
      modelActivado = !modelActivado;

      // Guardar el nuevo estado en localStorage
      localStorage.setItem('model_activado', modelActivado);

      // Cambiar el texto del botón dependiendo del estado
      if (modelActivado) {
        conectarButton.textContent = 'true'; // Puedes cambiar el texto según tu preferencia
      } else {
        conectarButton.textContent = 'false'; // Puedes cambiar el texto según tu preferencia
      }

      // Verificar que se guardó correctamente (opcional)
      console.log('model_activado:', localStorage.getItem('model_activado'));
    }

    // Configurar el evento de clic para alternar el estado
    conectarButton.addEventListener('click', toggleModelState);
  }
});





















////////////////////////BOTONES DE COLOR////////////////////////////
////////////////////////////////////////////////////////////////
// Referencias a los botones
const btnGris = document.getElementById('btnGris');
const btnVerde = document.getElementById('btnVerde');

 // Evento para cambiar el color del botón gris
btnGris.addEventListener('click', () => {
  btnGris.classList.toggle('activo'); // Cambia entre gris y verde
  const isActive = btnGris.classList.contains('activo');
  localStorage.setItem('activado_voz', JSON.stringify(isActive)); // Guarda el estado como cadena JSON
  alert(isActive ? 'Voz activada' : 'Voz desactivada');
});

// Evento para cambiar el color del botón verde
btnVerde.addEventListener('click', () => {
  btnVerde.classList.toggle('activo'); // Cambia entre verde y azul
  const isActive = btnVerde.classList.contains('activo');
  localStorage.setItem('idioma_es', JSON.stringify(isActive)); // Guarda el estado como cadena JSON
  alert(isActive ? 'Spanish activado' : 'Spanish desactivado');
});




