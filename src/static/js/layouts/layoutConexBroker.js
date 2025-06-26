<<<<<<< HEAD

function verificarYActualizarEstado() {
    let account = localStorage.getItem('cuenta');
    
    fetch(`/herramientasSheet_accionesSheet_actualizaLuz_websocket?account=${account}`)
        .then(response => response.json())
        .then(data => {
            actualizarEstado_luz_ws(data);
            control_conexion_ws();
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

  
  


function control_conexion_ws() {
    var luzWebsocket_control = localStorage.getItem('luzWebsocket_control');
    
    // Si el valor es 'True', cambiar el color y el mensaje
    if (luzWebsocket_control == 'True') {
        document.getElementById('labelLayout').style.backgroundColor = '#5eff00';  // Verde
        document.querySelector('#labelLayout label').textContent = 'Conexión a broker establecida';
    } 
    // Si el valor es 'False', cambiar el color a rojo y el mensaje a "fuera de línea"
    else if (luzWebsocket_control == 'False') {
        document.getElementById('labelLayout').style.backgroundColor = '#ff0000';  // Rojo
        document.querySelector('#labelLayout label').textContent = 'Fuera de línea';
    } 
    // Si no hay valor, puedes dejar el color y mensaje predeterminado o manejar otro caso
    else {
        document.getElementById('labelLayout').style.backgroundColor = '#f8f9fa';  // Gris claro
        document.querySelector('#labelLayout label').textContent = 'Estado de conexión desconocido';
    }
}

verificarYActualizarEstado();
=======

function verificarYActualizarEstado() {
    let account = localStorage.getItem('cuenta');
    
    fetch(`/herramientasSheet_accionesSheet_actualizaLuz_websocket?account=${account}`)
        .then(response => response.json())
        .then(data => {
            actualizarEstado_luz_ws(data);
            control_conexion_ws();
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

  
  


function control_conexion_ws() {
    var luzWebsocket_control = localStorage.getItem('luzWebsocket_control');
    
    // Si el valor es 'True', cambiar el color y el mensaje
    if (luzWebsocket_control == 'True') {
        document.getElementById('labelLayout').style.backgroundColor = '#5eff00';  // Verde
        document.querySelector('#labelLayout label').textContent = 'Conexión a broker establecida';
    } 
    // Si el valor es 'False', cambiar el color a rojo y el mensaje a "fuera de línea"
    else if (luzWebsocket_control == 'False') {
        document.getElementById('labelLayout').style.backgroundColor = '#ff0000';  // Rojo
        document.querySelector('#labelLayout label').textContent = 'Fuera de línea';
    } 
    // Si no hay valor, puedes dejar el color y mensaje predeterminado o manejar otro caso
    else {
        document.getElementById('labelLayout').style.backgroundColor = '#f8f9fa';  // Gris claro
        document.querySelector('#labelLayout label').textContent = 'Estado de conexión desconocido';
    }
}

verificarYActualizarEstado();
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
