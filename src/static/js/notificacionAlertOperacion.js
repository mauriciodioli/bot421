
// Solicitar permiso para mostrar notificaciones
function solicitarPermiso() {
    if (Notification.permission !== "granted") {
        Notification.requestPermission().then(permission => {
            if (permission === "granted") {
                console.log("Permiso concedido para mostrar notificaciones.");
            }
        });
    }
}

// Mostrar una notificación
function mostrarNotificacion(dato) {
    //console.log(Notification.permission)
    if (Notification.permission === "granted") {
        const tituloOriginal = "¡Operación nueva!";
        const tituloModificado = dato[0].replace('MERV - XMEV -','')+' - '+dato[4]+' - '+dato[3]; // Modifica el título de la notificación

        const notificacion = new Notification(tituloOriginal, {
            body: tituloModificado + "\n¡Debe operar nuevamente!", // Agrega el título modificado al cuerpo de la notificación
            icon: "/static/img/icono.png"
        });

        // Puedes añadir un evento click para que algo suceda cuando se hace clic en la notificación
        notificacion.onclick = function(event) {
            window.focus(); // Lleva al usuario a la ventana que generó la notificación
            event.target.close(); // Cierra la notificación
            // Aquí puedes agregar el código que quieres que se ejecute al hacer clic en la notificación
        };
    }
}
