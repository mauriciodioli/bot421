 // Obtener el enlace "Signals"
 document.getElementById('openModalSignals').addEventListener('click', function (e) {
    // Prevenir el comportamiento por defecto (enlace)
    e.preventDefault();
    // Abrir el modal
    var myModal = new bootstrap.Modal(document.getElementById('modalSeleccionPais'));
    myModal.show();
});




function mostrarSplash() {
    document.getElementById("splash").style.display = "block";
  }

  document.getElementById('guardarPais').addEventListener('click', function() {
    document.getElementById('splash').style.display = 'block';
   
    var selectedCountry = document.getElementById('seleccionarPais').value;
    var usuario_id ='demo';
    access_token = 'access_dpi_token_usuario_anonimo';
    refresh_token = 'access_dpi_refresh_token';
    var selector = localStorage.getItem('selector');
    localStorage.setItem('paisSeleccionado', selectedCountry);
    $('#modalSeleccionPais').modal('hide'); // Esta línea cierra el modal
     // Redirigir a la ruta /panel_control_sin_cuenta
    layoutOrigen = 'layout_dpi'; // Cambia 'nombre_del_layout' por el valor deseado
    var url = '/panel_control_sin_cuenta?country=' + selectedCountry + '&layoutOrigen=' + layoutOrigen+ '&usuario_id=' + usuario_id+'&access_token='+access_token+'&refresh_token='+refresh_token+'&selector='+selector;
    window.location.href = url;
  });   
// en este script cargo el correo electrónico almacenado en el localStorage
access_token = 'access_dpi';
correo_electronico = 'desde_dpi_acceso_anonimo';

$(document).ready(function() {
// Escuchar el evento de cambio en el combobox 1
$("#selctorEnvironment1").change(function() {
  // Obtener el valor seleccionado
  
  var selectedValue = $(this).val();


  // Asignar el valor al campo de entrada oculto "environment" en el formulario 1
  $("input[name='broker_id']").val(selectedValue);
});

// Escuchar el evento de cambio en el combobox 2
$("#selctorEnvironment2").change(function() {
  // Obtener el valor seleccionado
  var selectedValue2 = $(this).val();
 

  // Asignar el valor al campo de entrada oculto "environment" en el formulario 2
  $("input[name='environment']").val(selectedValue2);
});

// Asignar el valor del access token al campo oculto en ambos formularios
$("input[name='access_token']").val(access_token);
$("input[name='access_token_form2']").val(access_token);
});


function cargarOpcionesCombo() {
// Realizar una solicitud Ajax para obtener las opciones del combo
fetch('/cuenta-endpoint-all/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        accessToken: access_token // Reemplaza 'TOKEN_AQUI' con el token adecuado
    })
})
.then(response => response.json())
.then(data => {
    const selectElement = document.getElementById('selctorEnvironment1');
    // Limpiar las opciones existentes
    selectElement.innerHTML = '';

    // Agregar la opción inicial
    const initialOption = document.createElement('option');
    initialOption.value = ''; // Opcional: puedes asignar un valor específico aquí si lo necesitas
    initialOption.textContent = 'Open this select menu';
    selectElement.appendChild(initialOption);

    // Agregar las nuevas opciones desde los datos obtenidos
    data.endpoints.forEach(endpoint => {
        const optionElement = document.createElement('option');
        optionElement.value = endpoint.id; // Cambiar por el valor correcto
        optionElement.textContent = endpoint.nombre; // Cambiar por el texto correcto
        selectElement.appendChild(optionElement);
    });

    // Agregar un event listener para el cambio en el selector de entorno
    selectElement.addEventListener('change', function() {
        // Obtener el valor y el texto seleccionados
        const selectedOption = this.options[this.selectedIndex];
        const brokerId = selectedOption.value;
        const brokerNombre = selectedOption.textContent;

        // Actualizar los campos ocultos con los valores seleccionados
        document.getElementById('broker_id').value = brokerId;
        document.getElementById('broker_nombre').value = brokerNombre;
    });
})
.catch(error => {
  console.error('Error al cargar opciones del combo:', error);
  alert('Hubo un problema al cargar las opciones del combo. Por favor, logee nuevamente en el sistema puede haber vencido el token de acceso o inténtalo de nuevo más tarde o contacta al soporte técnico.');
});
}



// Llamar a la función para cargar las opciones del combo cuando la página se cargue
//window.addEventListener('DOMContentLoaded', cargarOpcionesCombo);



