

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
  
          mediaElement.addEventListener('click', function() {
            openMediaModal(e.target.result, file.type);
          });
          mediaContainer.appendChild(mediaElement);
        };
  
        reader.readAsDataURL(file);
      }
    });
  
    function openMediaModal(src, type) {
      if (type.startsWith('image/')) {
        modalImage.src = src;
        mediaModal.style.display = 'block';
  
        // Inicializar Cropper.js
        cropper = new Cropper(modalImage, {
          aspectRatio: 16 / 9, // Ajusta la relación de aspecto según sea necesario
          viewMode: 1,
          autoCropArea: 1,
          cropBoxResizable: true,
          cropBoxMovable: true,
          movable: true,
        });
      } else if (type.startsWith('video/')) {
        modalImage.src = ''; // Clear image when opening video
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
  
          // Eliminar la imagen original
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
  
  $(document).ready(function() {
    var storedFiles = []; // Array para almacenar todos los archivos seleccionados
  
    // Evento cuando se seleccionan archivos
    $("#fileInput_creaPublicacion").on("change", function(event) {
      var files = event.target.files;
  
      // Crear un mapa de archivos basado en el nombre del archivo
      var fileMap = {};
  
      // Añadir archivos ya almacenados al mapa
      storedFiles.forEach(file => {
        fileMap[file.name] = file;
      });
  
      // Añadir archivos nuevos al mapa, reemplazando si ya existe
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        fileMap[file.name] = file;
      }
  
      // Convertir el mapa de archivos de nuevo a un array
      storedFiles = Object.values(fileMap);
    
      // Opcional: puedes mostrar una vista previa de los archivos seleccionados aquí
    });
  
    $("#createPostForm_creaPublicacion").on("submit", function(event) {
      event.preventDefault(); // Prevent the default form submission
  
      var formData = new FormData(this);
  
      // Añadir datos adicionales al FormData
      var access_token = localStorage.getItem('access_token');
      var correo_electronico = localStorage.getItem('correo_electronico');
      var color_texto = 'black';
      var color_titulo = 'black';
     
  
      // Añadir los datos al FormData
      formData.append('correo_electronico', correo_electronico);
      formData.append('color_texto', color_texto);
      formData.append('color_titulo', color_titulo);
  
      // Añadir todos los archivos almacenados en storedFiles al FormData
      storedFiles.forEach((file, index) => {
        formData.append(`mediaFile_${index}`, file);
        formData.append(`mediaFileSize_${index}`, file.size);
        formData.append(`mediaFileIndex_${index}`, index);
        formData.append(`mediaFileName_${index}`, file.name);
        formData.append(`mediaFileType_${index}`, file.type);
        formData.append(`mediaFileLastModified_${index}`, file.lastModified);
        formData.append(`mediaFileLastModifiedDate_${index}`, file.lastModifiedDate ? file.lastModifiedDate.toISOString() : 'No disponible');
        formData.append(`mediaFileWebkitRelativePath_${index}`, file.webkitRelativePath || 'No disponible');
      });
  
      // Limpiar storedFiles después de enviar
      storedFiles = [];
  
  
        $.ajax({
          // Configuración de la solicitud AJAX
          url: '/social_imagenes_crear_publicacion',
          type: 'POST',
          data: formData,
          processData: false,
          contentType: false,
          headers: {
            'Authorization': 'Bearer ' + access_token
          },
          success: function(response) {
            if (Array.isArray(response)) {
                var postDisplayContainer = $('#postDisplayContainer');
                postDisplayContainer.empty();
                $('#createPostModal_creaPublicacion').hide();
        
                response.forEach(function(post) {
                    if (post.imagenes.length > 0 || post.videos.length > 0) {
                        var mediaHtml = '';
                        var baseUrl = window.location.origin;
        
                        if (Array.isArray(post.imagenes) && post.imagenes.length > 0) {
                            // Mostrar solo la primera imagen
                            var firstImageUrl = baseUrl + '/' + post.imagenes[0].filepath;
                            mediaHtml += `<img src="${firstImageUrl}" alt="Imagen de la publicación" onclick="abrirModal(${post.publicacion_id})">`;
        
                            // Guardar las demás imágenes para mostrarlas en el modal
                            var modalImagesHtml = '';
                            post.imagenes.forEach(function(image, index) {
                                if (index > 0) { // Saltar la primera imagen
                                    var imageUrl = baseUrl + '/' + image.filepath;
                                    modalImagesHtml += `<img src="${imageUrl}" alt="Imagen de la publicación" class="imagen-muestra-crea-publicacion">`;
                                }
                            });
        
                            // Crear el HTML del modal con el sufijo muestra-crea-publicacion
                            var modalHtml = `
                                <div class="modal-muestra-crea-publicacion" id="modal-${post.publicacion_id}" style="display:none;">
                                    <div class="modal-content-muestra-crea-publicacion">
                                        <span class="close-muestra-crea-publicacion" onclick="cerrarModal(${post.publicacion_id})">&times;</span>
                                        <div class="modal-image-grid-muestra-crea-publicacion">
                                            ${modalImagesHtml}
                                        </div>
                                    </div>
                                </div>
                            `;
        
                            postDisplayContainer.append(modalHtml);
                        }
        
                        var estadoClass;
                        var estadoTextClass;
                        switch (post.estado) {
                            case 'activo':
                                estadoClass = 'estado-activo';
                                estadoTextClass = 'estado-activo';
                                break;
                            case 'inactivo':
                                estadoClass = 'estado-inactivo';
                                estadoTextClass = 'estado-inactivo';
                                break;
                            case 'pendiente':
                                estadoClass = 'estado-pendiente';
                                estadoTextClass = 'estado-pendiente';
                                break;
                            default:
                                estadoClass = '';
                                estadoTextClass = '';
                        }
        
                        var cardHtml = `
                            <div class="card-publicacion-admin ${estadoClass}" id="card-${post.publicacion_id}" onclick="cambiarEstado(event, ${post.publicacion_id})">
                                <div class="card-body">
                                    <h5 class="card-title">${post.titulo}</h5>
                                    <p class="card-text-estado ${estadoTextClass}">${post.estado}</p>
                                    <p class="card-text">${post.correo_electronico}</p>
                                    <p class="card-date">${formatDate(post.fecha_creacion)}</p>
                                    <p class="card-text">${post.texto}</p>
                                    <div class="card-media-grid-publicacion-admin">
                                        ${mediaHtml}
                                    </div>
                                    <p class="card-text">${post.ambito}</p>
                                    <p class="card-text">${post.descripcion}</p>
                                    <div class="btn-modificar-eliminar">
                                        <button class="btn-modificar" onclick="modificarPublicacion(${post.publicacion_id})">Modificar</button>
                                        <button class="btn-eliminar" onclick="eliminarPublicacion(${post.publicacion_id})">Eliminar</button>
                                    </div>
                                </div>
                            </div>
                        `;
        
                        postDisplayContainer.append(cardHtml);
                    } else {
                        console.log('Publicación sin contenido:', post.publicacion_id);
                    }
                });
            } else {
                console.error("La respuesta no es un array. Recibido:", response);
            }
        },      
          error: function(xhr, status, error) {
            alert("Error al cargar las publicaciones. Inténtalo de nuevo.");
          }
        });
    });
  
    function dataURLToFile(dataURL, filename) {
      var arr = dataURL.split(','), mime = arr[0].match(/:(.*?);/)[1],
          bstr = atob(arr[1]), n = bstr.length, u8arr = new Uint8Array(n);
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n);
      }
      return new File([u8arr], filename, {type: mime});
    }
  });
  