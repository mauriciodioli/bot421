function setFichaData(fichaId,idFicha) {
    accessToken = localStorage.getItem('access_token');
    access_token_element = document.getElementById('recibir_access_token');
    eliminarFichaId_element = document.getElementById('recibirFichaId');
    recibirIdFicha_element = document.getElementById('recibiridFicha');
   // Verifica si los elementos existen antes de intentar establecer sus valores
   if (access_token_element && eliminarFichaId_element) {
       access_token_element.value = accessToken;
       eliminarFichaId_element.value = fichaId;
       recibirIdFicha_element.value = idFicha
   } else {
       console.error("Elementos no encontrados.");
   }
}
 //esto es para el modal de llave
 function setFichaDataToken( llave,monto) {
  
   document.getElementById('llaveFicha').textContent = llave;
   document.getElementById('montoFicha').textContent = monto;
}



////cuando se abre el modal se llama la funcion para cargar los usuarios
var seleccionarUsuarioModal = document.getElementById('seleccionarUsuarioModal');
if (seleccionarUsuarioModal) {
   seleccionarUsuarioModal.addEventListener('shown.bs.modal', function () {
       cargarUsuarios();
   });
}




   function setFichaDataReportar(fichaId,idFicha) {
       var accessToken = localStorage.getItem('access_token');
       var access_token_element = document.getElementById('access_token');
       var reportarFichaId_element = document.getElementById('reportarFichaId');
       var reportarIdFicha_element = document.getElementById('reportaridFicha');
      
       // Verifica si los elementos existen antes de intentar establecer sus valores
      
           access_token_element.value = accessToken;
           reportarFichaId_element.value = fichaId;
           reportarIdFicha_element.value = idFicha;
       
 }





   document.addEventListener('DOMContentLoaded', function() {
     var IngresaValorFicha = document.getElementById('IngresaValorFicha');
     // Obtener todas las filas de la tabla
     var filas = Array.from(document.querySelectorAll('tr')).slice(1); // Saltar la primera fila

       if (IngresaValorFicha) {
           IngresaValorFicha.addEventListener('click', function() {
               document.getElementById('tokenInput').value = '';
               document.getElementById('valorllave').textContent = '';
           });
       
           var aceptarBtn = document.getElementById('aceptarBtn');
           var tomarFichaForm = document.getElementById('tomarFicha');
           
           aceptarBtn.addEventListener('click', function() {
               // Obtener el valor del token ingresado
               var tokenInputValue = document.getElementById('tokenInput').value;
       
               // Verificar si el valor es un número y no está vacío
               if (!isNaN(tokenInputValue) && tokenInputValue.trim() !== '') {
                   var tokenForm = localStorage.getItem('access_token');
                   var layoutOrigen = "{{ layout }}";
                   document.getElementById('layoutOrigen').value = layoutOrigen;
                   document.getElementById('access_token_forma').value = tokenForm;
       
                   // Envía el formulario
                   tomarFichaForm.submit();
               } else {
                   // Muestra un mensaje de error o toma la acción que desees
                   alert('Ingresa un número válido en el campo del token.');
               }
           });
         } 
         
         

         filas.forEach(function(fila) {
            // Obtener el elemento <th> dentro de la fila
            var thElement = fila.querySelector('th');
        
            // Verificar si el elemento <th> existe
            if (thElement) {
                // Obtener la fecha de traspaso desde el <th>
                var fechaTraspaso = thElement.innerText;
        
                if (fechaTraspaso) {
                    // Calcular los días pasados
                    var dias = calcularDias(fechaTraspaso);
        
                    // Actualizar el contenido del <th>
                    thElement.innerText = ` ${dias}`;
                }
            } else {
                console.error('No se encontró un elemento <th> en la fila:', fila);
            }
        });










   });
   


   function calcularDias(fechaTraspaso) {
    // Convertir la fecha de traspaso a un objeto Date de JavaScript
    var fechaTraspasoDate = new Date(fechaTraspaso);
    var fechaActual = new Date();

    // Calcular la diferencia en milisegundos
    var diferenciaMilisegundos = fechaActual - fechaTraspasoDate;

    // Convertir la diferencia a días
    var diasPasados = Math.floor(diferenciaMilisegundos / (1000 * 60 * 60 * 24));

    return diasPasados;
}