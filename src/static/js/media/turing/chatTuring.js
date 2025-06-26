function obtenerChatUsuariosPregunta() {
  
   
    if ( localStorage.getItem('usuario_id_chat') === 'undefined' || localStorage.getItem('pregunta_id_bucle') === null) {
        // Si no está configurado o es indefinido, lo inicializa con el valor 1
        localStorage.setItem('usuario_id_chat', '1');
      }
      
      id = localStorage.getItem('usuario_id_chat');
    
    id = localStorage.getItem('usuario_id_chat');
    $.ajax({
        url: '/turing-turingUser-obtener-id/' + id,
        method: 'GET',
        success: function (data) {
            if (splash) {
                splash.style.display = 'none'; // Ocultar el splash al terminar
            }
            // Limpiar el contenido del input antes de cerrar el modal
            //document.getElementById('preguntaInput').value = ''; // Limpiar el input
            // Cerrar el modal una vez que la petición sea exitosa
            //$('#preguntaModal').modal('hide'); // Usando Bootstrap para cerrar el modal
          
            // Verificar si no se encontraron datos
            if (data.not_found) {
                // Incrementar el valor almacenado en localStorage
                const usuarioIdChat = localStorage.getItem('usuario_id_chat') || 0; // Si no existe, inicia en 0
                const Incrementar = parseInt(usuarioIdChat) + 1;
                if (data.max_id < Incrementar) {
                    localStorage.setItem('usuario_id_chat', 2);
                }else{                  
                  localStorage.setItem('usuario_id_chat', Incrementar); // Sumar 1
                }
            } else {
                // Procesar los datos normalmente si se encontraron
                const nombre = data.nombre;
                const descripcion = data.descripcion;
                const fechaCreacion = new Date().toLocaleString(); // Si no tienes la fecha, usa la fecha actual
                                
                 // Incrementar el valor almacenado en localStorage
                 const usuarioIdChat = localStorage.getItem('usuario_id_chat') || 0; // Si no existe, inicia en 0
                 const Incrementar = parseInt(usuarioIdChat) + 1;
                 if (data.max_id < Incrementar) {
                     localStorage.setItem('usuario_id_chat', 2);
                 }else{                  
                   localStorage.setItem('usuario_id_chat', Incrementar); // Sumar 1
                 }
                 //localStorage.setItem('usuario_id_chat', data.id);
                // Llamar a la función para agregar la pregunta a la lista
               // console.log(data);
                if (data.nombre&&data.descripcion) {
                    const fechaCreacion = new Date().toLocaleString(); // Si no tienes la fecha, usa la fecha actual
                   
                    if (data.fechaCreacion) {
                        fechaCreacion = data.fechaCreacion;
                    }

                    agregarPreguntaUsuarioListaDePreguntas(data.nombre, data.descripcion, data.idioma, fechaCreacion);
                } else {
                    
                    console.error('en chatTuring js No se recibió respuesta:', data);
                }
            }
        },
        error: function () {
            console.error('Error al obtener la pregunta');
        }
    });
}



// Función para agregar la pregunta a la lista
function agregarPreguntaUsuarioListaDePreguntas(nombre, descripcion, idioma, fechaCreacion) {
   
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






