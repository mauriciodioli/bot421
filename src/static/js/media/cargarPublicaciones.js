

  // Get the modal
  var modal = document.getElementById("createPostModal_creaPublicacion");

  // Get the button that opens the modal
  var btn = document.getElementById("createPostBtn_creaPublicacion");
  
  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close_creaPublicacion")[0];
  
  // When the user clicks the button, open the modal 
  btn.onclick = function() {
    modal.style.display = "block";
  }
  
  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modal.style.display = "none";
  }
  
  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
  }
  
  
  
  
  
  document.addEventListener('DOMContentLoaded', function() {
    initializeMediaHandlers();
   
  });
  
  function initializeMediaHandlers() {
    var fileInput = document.getElementById('fileInput_creaPublicacion');
    var mediaContainer = document.getElementById('mediaContainer_creaPublicacion');
    var mediaModal = document.getElementById('imageModal_creaPublicacion');
    var modalImage = document.getElementById('modalImage_creaPublicacion');
    var closeMediaModal = document.querySelector('.close-image_creaPublicacion');
    var cropper;
  
    fileInput.addEventListener('change', function(event) {
      var files = event.target.files;
  
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        var reader = new FileReader();
  
        reader.onload = function(e) {
          var mediaElement;
          var mediaWrapper = document.createElement('div');
          mediaWrapper.classList.add('media-wrapper_creaPublicacion'); // Envoltorio para el elemento multimedia y el botón de cerrar

          if (file.type.startsWith('image/')) {
            mediaElement = document.createElement('img');
            mediaElement.src = e.target.result;
            mediaElement.classList.add('thumbnail_creaPublicacion');            
          } else if (file.type.startsWith('video/')) {
            mediaElement = document.createElement('video');
            mediaElement.src = e.target.result;
            mediaElement.controls = true;
            mediaElement.classList.add('thumbnail_creaPublicacion');
          }
          var closeButton = document.createElement('button');
          closeButton.textContent = '×';
          closeButton.classList.add('close-button_creaPublicacion'); // Clase para estilizar el botón de cerrar
          closeButton.addEventListener('click', function() {
              mediaWrapper.remove(); // Elimina el elemento multimedia del contenedor
          });
          mediaElement.addEventListener('click', function() {
            openMediaModal(e.target.result, file.type);
          });
          mediaWrapper.appendChild(mediaElement); // Añade el elemento multimedia al contenedor
          mediaWrapper.appendChild(closeButton); // Añade el botón de cerrar al contenedor
      
          mediaContainer.appendChild(mediaWrapper);
        };
  
        reader.readAsDataURL(file);
      }
    });
  



 // Función para mostrar vista previa de archivos



    /**
     * Abre el modal para mostrar el archivo seleccionado y permite recortar
     * las imágenes.
     * @param {string} src URL del archivo seleccionado
     * @param {string} type Tipo de archivo (image/* o video/*)
     */
    function openMediaModal(src, type) {
      if (type.startsWith('image/')) {
        modalImage.src = src;
        mediaModal.style.display = 'block';
    
        cropper = new Cropper(modalImage, {
          aspectRatio: 16 / 9,
          viewMode: 1,
          autoCropArea: 1,
          cropBoxResizable: true,
          cropBoxMovable: true,
          movable: true,
        });
    
        // Manejar el evento de cierre del modal
        mediaModal.addEventListener('hidden.bs.modal', function() {
          if (cropper) {
            var canvas = cropper.getCroppedCanvas();
            if (canvas) {
              canvas.toBlob(function(blob) {
                if (blob) {
                  var originalFileName = src.split('/').pop();
                  var newFileName = originalFileName.replace(/(\.[\w\d_-]+)$/i, '-copia$1');
                  var croppedFile = new File([blob], newFileName, { type: 'image/jpeg', lastModified: Date.now() });
        
                  // Asegúrate de que la imagen recortada se añade al contenedor de medios
                  var img = document.createElement('img');
                  img.src = URL.createObjectURL(blob);
                  img.classList.add('thumbnail_creaPublicacion');
                  mediaContainer.appendChild(img);
        
                  // Aquí, actualiza la lista de archivos si es necesario
                  reemplazarImagenOriginal(croppedFile, src);
                }
              }, 'image/jpeg');
            }
            cropper.destroy();
          }
        }, { once: true });
        
      } else if (type.startsWith('video/')) {
        modalImage.src = '';
        modalImage.innerHTML = `<video src="${src}" controls style="max-width: 100%; max-height: 100%;"></video>`;
      }
    }
    
    
    
  
  
  
    function saveCroppedImage() {
      if (cropper) {
        cropper.getCroppedCanvas().toBlob(function(blob) {
          var url = URL.createObjectURL(blob);
          var img = document.createElement('img');
          img.src = url;
          img.classList.add('thumbnail_creaPublicacion');
    
          // Añadir la imagen recortada al contenedor de medios en el modal de creación
          mediaContainer.appendChild(img);
    
          // Asegurar que la imagen recortada se puede abrir en el modal
          img.addEventListener('click', function() {
            openMediaModal(url, 'image/');
          });
    
          // Eliminar la imagen original del contenedor
          var thumbnails = mediaContainer.getElementsByClassName('thumbnail_creaPublicacion');
          for (var i = 0; i < thumbnails.length; i++) {
            if (thumbnails[i].src === modalImage.src) {
              mediaContainer.removeChild(thumbnails[i]);
              break;
            }
          }
    
          // Cerrar el modal de edición y eliminar el cropper
          mediaModal.style.display = 'none';
          cropper.destroy();
        });
      }
    }
    
  
    closeMediaModal.addEventListener('click', function() {
      mediaModal.style.display = 'none';
      if (cropper) {
        cropper.destroy();
      }
    });
  
    
    document.getElementById('saveCroppedImage').addEventListener('click', saveCroppedImage);
  }
  
  
  
  
  function closePreview() {
    deb
    var previewImage = document.getElementById('preview-image-media_imagenes');
    var fileInput = document.getElementById('imagen-media_imagenes');
    var uploadButton = document.getElementById('open-popup-media_imagenes');
  
    previewImage.src = '#'; // Limpiar la imagen
    fileInput.value = ''; // Limpiar el campo de entrada de archivos
    var closeButton = document.querySelector('.close-button-media_imagenes');
    closeButton.style.display = 'none'; // Ocultar el botón de cerrar
    uploadButton.disabled = true; // Deshabilitar el botón
  }
  
  
  
  function dataURLToFile(dataURL, filename) {
    var arr = dataURL.split(',');
    var mime = arr[0].match(/:(.*?);/)[1];
    var bstr = atob(arr[1]);
    var n = bstr.length;
    var u8arr = new Uint8Array(n);
    while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
    }
    return new File([u8arr], filename, { type: mime });
  }



  function reemplazarImagenOriginal(croppedFile, originalSrc) {

      // Encuentra el índice del archivo original en el array de archivos almacenados
      const originalIndex = storedFiles.findIndex(file => file.name === originalSrc.split('/').pop());
    
      // Si el archivo original existe, reemplázalo con el archivo recortado
      if (originalIndex !== -1) {
        storedFiles.splice(originalIndex, 1, croppedFile);
      }
      
      // Aquí puedes actualizar la vista si es necesario
      // Por ejemplo, actualizar el DOM o la vista previa de archivos
    }
    
    
  
  






















 /**************************************************************************/
/**************************************************************************/
/*******************AQUI SE CREA LAS PUBLICACIOENS*************************/
/*******************DESDE MOSTRARGALERIA.HTML******************************/
/**************************************************************************/
$(document).ready(function () {
  var storedFiles = [];
  var CHUNK_SIZE = 1024 * 1024; // 1 MB por fragmento
  var progressBar = $("#progressBar");
  var progressText = $("#progressText");

  $("#fileInput_creaPublicacion").on("change", function (event) {
    storedFiles = Array.from(event.target.files);
  });

  $("#createPostForm_creaPublicacion").on("submit", function (event) {
    event.preventDefault();
    document.getElementById("loader-modal-crear-publicacion").style.display = "block";

    var access_token = localStorage.getItem("access_token");
    var totalSize = storedFiles.reduce((sum, file) => sum + file.size, 0);
    var uploadedSize = 0;
    var minDisplayTime = 500; // Tiempo mínimo en ms para que la barra sea visible
    var startTime = Date.now();

    $(".splashCarga").show();

    async function uploadChunk(file, start) {
      try {
        var end = Math.min(start + CHUNK_SIZE, file.size);
        var chunk = file.slice(start, end);
        var isLastChunk = end === file.size;

        var formData = new FormData();
        formData.append("chunk", chunk);
        formData.append("fileName", file.name);
        formData.append("fileSize", file.size);
        formData.append("fileType", file.type);
        formData.append("chunkStart", start);
        formData.append("isLastChunk", isLastChunk);
        formData.append("content_type", file.type || "application/octet-stream");

        await $.ajax({
          url: "/social_publicaciones_handle_upload_chunkn/",
          type: "POST",
          data: formData,
          processData: false,
          contentType: false,
          headers: { Authorization: "Bearer " + access_token },
        });

        uploadedSize += chunk.size;

        // Actualizar la barra de progreso con el progreso total de todos los archivos
        var progress = Math.min((uploadedSize / totalSize) * 100, 100);
        progressBar.css("width", progress + "%");
        progressText.text(`Cargando... ${progress.toFixed(2)}%`);

      } catch (error) {
        $(".splashCarga").hide();
        console.error(`Error al cargar el fragmento del archivo "${file.name}"`, error);
        throw error;
      }
    }

    async function uploadFile(file) {
      var start = 0;
      while (start < file.size) {
        await uploadChunk(file, start);
        start += CHUNK_SIZE;
      }
    }

    (async function uploadAllFiles() {
      try {
        for (let file of storedFiles) {
          await uploadFile(file);
        }

        let elapsedTime = Date.now() - startTime;
        if (elapsedTime < minDisplayTime) {
          await new Promise(resolve => setTimeout(resolve, minDisplayTime - elapsedTime));
        }

        createPost(event, storedFiles);
      } catch (error) {
        $(".splashCarga").hide();
        console.error("Error al cargar archivos:", error);
        alert("Hubo un error durante la carga");
      } finally {
        console.log("Carga finalizada");
      }
    })();
  });
});


function createPost(event,storedFiles) { 
    
     event.preventDefault(); // Evitar el envío predeterminado del formulario
  // Definir y inicializar mediaContainer
     var mediaContainer = document.getElementById('mediaContainer_creaPublicacion');
  // Obtener datos del formulario
     var formData = new FormData(event.target); // Usar el formulario que ha disparado el evento
      // Añadir datos adicionales al FormData
      var access_token = localStorage.getItem('access_token');
      var correo_electronico = localStorage.getItem('correo_electronico');
      var color_texto = 'black';
      var color_titulo = 'black';
      var layout = 'layout'
      var ambito = localStorage.getItem('dominio');
     
  
      // Añadir los datos al FormData
      formData.append('correo_electronico', correo_electronico);
      formData.append('color_texto', color_texto);
      formData.append('color_titulo', color_titulo);
      formData.append('layout',layout);
      formData.append('ambito', ambito);
     
     
      // Añadir los metadatos de los archivos
      storedFiles.forEach(file => {
        formData.append('uploadedFilesMetadata', JSON.stringify({
          fileName: file.name,
          fileSize: file.size,
          content_type: file.type
        }));
      });

      setTimeout(function() { 
        $.ajax({
          // Configuración de la solicitud AJAX
          url: '/social_publicaciones_crear_publicacion_partes/',
          type: 'POST',
          data: formData,
          processData: false,
          contentType: false,
          timeout: 30000,  // 30 segundos
          headers: {
            'Authorization': 'Bearer ' + access_token
          },
          success: function(response) {           
            
                   
        if (Array.isArray(response)) {
          var postAccordion = $('#postAccordion');
          postAccordion.empty();
  
          // Crear un objeto para almacenar las publicaciones por ámbito
          var postsByAmbito = {};
          // Iterar sobre las publicaciones para organizarlas por ámbito
          response.forEach(function(post) {
              if (!postsByAmbito[post.ambito]) {
                  postsByAmbito[post.ambito] = [];
              }
              postsByAmbito[post.ambito].push(post);
          });
        
          // Crear secciones del acordeón para cada ámbito
          Object.keys(postsByAmbito).forEach(function(ambito, index) {
              var ambitoId = 'ambito-' + index; // ID único para cada ámbito
              var publicaciones = postsByAmbito[ambito];
              
              var accordionItemHtml = `
                  <div class="accordion-item">
                      <h2 class="accordion-header" id="heading-${ambitoId}">
                          <button class="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${ambitoId}" aria-expanded="true" aria-controls="collapse-${ambitoId}">
                              ${ambito}
                          </button>
                      </h2>
                      <div id="collapse-${ambitoId}" class="accordion-collapse collapse ${index === 0 ? 'show' : ''}" aria-labelledby="heading-${ambitoId}" data-bs-parent="#postAccordion">
                          <div class="accordion-body">
                              <div id="accordion-content-${ambitoId}" class="accordion-content">
                                  <div class="card-grid-publicaciones"> <!-- Aquí se aplica la clase de grilla -->
                                  </div>
                              </div>
                          </div>
                      </div>
                  </div>
              `;
  
              postAccordion.append(accordionItemHtml);
  
              var accordionContent = $(`#accordion-content-${ambitoId} .card-grid-publicaciones`);
  
              // Agregar publicaciones al acordeón correspondiente
              publicaciones.forEach(function(post) {
                  var mediaHtml = '';
                  //var baseUrl = window.location.origin;
  
                  if (Array.isArray(post.imagenes) && post.imagenes.length > 0  || post.videos.length > 0) {
                      
                    if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                        // Si hay imágenes, usar la primera
                      
                       if (post.imagenes[0].imagen != null) {
                            var firstImageBase64 = post.imagenes[0].imagen;
                            var firstImageUrl = `data:${post.imagenes[0].mimetype};base64,${firstImageBase64}`;
                             mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
                       } else {
                            var firstImageUrl = post.imagenes[0].filepath;

                            console.log(post.imagenes[0].filepath);
                            mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
                       }
                      } else if (Array.isArray(post.videos) && post.videos.length > 0) {
                     
                        // Si no hay imágenes pero hay videos, usar el primero
                        var firstVideoUrl = post.videos[0].filepath;
                        console.log(post.videos[0].filepath);
                        mediaHtml += `
                                <video controls onclick="abrirModal(${post.publicacion_id})">
                                    <source src="${firstVideoUrl}" type="video/mp4">                                           
                                    Tu navegador no soporta la reproducción de videos.
                                </video>
                            `;
                    } else {
                        // Si no hay ni imágenes ni videos, mostrar un mensaje o imagen por defecto
                        mediaHtml += `<p>No hay contenido multimedia disponible.</p>`;
                    }
               
                }
  
                  var cardHtml = `
                      <div class="card-publicacion-admin" id="card-${post.publicacion_id}" onclick="cambiarEstado(event, ${post.publicacion_id})">
                          <div class="card-body">
                              <h5 class="card-title">${post.titulo}</h5>
                              <p class="card-text-estado">${post.estado}</p>
                              <p class="card-text-email">${post.correo_electronico}</p>
                              <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                              <p class="card-text">${post.texto}</p>
                              <div class="card-media-grid-publicacion-admin">
                                  ${mediaHtml}
                              </div>
                              <p class="card-text-ambito">${post.ambito}</p>
                              <p class="card-text-descripcion">${post.descripcion}</p>
                              <div class="btn-modificar-eliminar">
                                  <button class="btn-modificar" onclick="modificarPublicacion(${post.publicacion_id})">Modificar</button>
                                  <button class="btn-eliminar" onclick="eliminarPublicacion(${post.publicacion_id})">Eliminar</button>
                              </div>
                          </div>
                      </div>
                  `;
  
                  accordionContent.append(cardHtml);
              });
          });
      } else {
        splash.style.display = 'none'; // Ocultar el splash al terminar
        console.log('Respuesta no válida');
      }

        // Finalizar carga
        finalizarCarga();
        modal.style.display = "none";  
        $(".splashCarga").hide();    
  },

                         
           
          
          
          error: function(xhr, status, error) {
            
           // splash.style.display = 'none'; // Ocultar el splash al terminar
            //modal.style.display = "none";
            // En la consola del navegador
            $(".splashCarga").hide();
            console.log(xhr.status); // Imprime el código de estado HTTP
            console.log(xhr.responseText); // Imprime el cuerpo de la respuesta
            console.log(error); // Imprime el mensaje de error
            alert("Error al cargar las publicaciones. Inténtalo de nuevo con otro nombre.");
          }
        });
      }, 100); // 100 ms de pausa antes de hacer la petición  

    
  
    function dataURLToFile(dataURL, filename) {
      var arr = dataURL.split(','), mime = arr[0].match(/:(.*?);/)[1],
          bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, {type: mime});
    }



  }








  function finalizarCarga() {
    // Obtener el modal y ocultarlo
    var modal = document.getElementById("createPostModal_creaPublicacion");
    if (modal) {
        modal.style.display = "none";
    }

    // Ocultar la pantalla de carga
    $(".splashCarga").hide();

    // Vaciar los campos del formulario
    var form = document.getElementById("createPostForm_creaPublicacion");
    if (form) {
        form.reset(); // Restablece todos los campos del formulario
    }

   
    // Resetear el campo de carga de archivos
    document.getElementById("fileInput_creaPublicacion").value = '';

    // Limpiar el input de creación de publicación en la vista principal
    document.getElementById("createPostBtn_creaPublicacion").value = '';

    // Opcional: Limpiar el menú desplegable de opciones personalizadas
    document.querySelector(".custom-dropdown-menu").innerHTML = '';

    console.log("Modal vaciado y cerrado correctamente.");

    var mediaContainer = document.getElementById('mediaContainer_creaPublicacion');
    while (mediaContainer.firstChild) {
        mediaContainer.removeChild(mediaContainer.firstChild);
    }

}















