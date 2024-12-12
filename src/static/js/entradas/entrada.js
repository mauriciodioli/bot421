 // Pasar los valores desde Flask al JavaScript
 

 // Obtener los valores de los inputs ocultos
    const dominio = document.getElementById('dominio').value;
    const pagina = document.getElementById('pagina').value;


 // Guardar en localStorage
 console.log("Dominio desde Flask:", dominio); // Depuración
 console.log("Página desde Flask:", pagina);  // Depuración
 debugger; 

 if ( !localStorage.getItem('dominio')) {
    localStorage.setItem('dominio', dominio);
    localStorage.setItem('pagina', pagina);
 }
 
 
$(document).ready(function() {
    // Función para enviar los datos de localStorage al servidor
    function sendLocalStorage() {
        // Mostrar el splash de espera
        var splash = document.querySelector('.splash_carga_publicaciones');

        if (splash) {
            splash.style.display = 'block'; // Mostrar el splash
        }
        var refresh_token = localStorage.getItem('refresh_token');
        var access_token = localStorage.getItem('access_token');
        var correo_electronico = localStorage.getItem('correo_electronico');
        var cuenta = localStorage.getItem("cuenta");
        var usuario = localStorage.getItem("usuario");
        var simuladoOproduccion = localStorage.getItem("selector");
        var dominio = localStorage.getItem('dominio');
        var pagina = localStorage.getItem('pagina');
        rutaDeLogeo = dominio;
        $.ajax({
            url: '/send_local_storage',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                'rutaDeLogeo': rutaDeLogeo,
                'refresh_token': refresh_token,
                'correo_electronico': correo_electronico,
                'cuenta': cuenta,
                'usuario': usuario,
                'access_token':access_token,
                'simuladoOproduccion': simuladoOproduccion
            }),
            success: function(data) {
                splash.style.display = 'none'; // Ocultar el splash al terminar
                if (data.success) {
                    console.log('data.ruta',data.ruta)
                   
                    window.location.href = `${data.ruta}/${data.dominio}`;  // Redirige a `index/personal`
                } else {
                    splash.style.display = 'none'; // Ocultar el splash al terminar
                    console.error("Error enviando los datos de localStorage");
                }
            },
            error: function(error) {
                splash.style.display = 'none'; // Ocultar el splash al terminar
                console.error("Error:", error);
            }
        });
    }

    // Llama a la función para enviar los datos de localStorage
    sendLocalStorage();
});