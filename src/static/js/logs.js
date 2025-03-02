// Función para obtener la IP del cliente y registrar el acceso
function obtenerIPYRegistrarAcceso() {
    // Utiliza ipify para obtener la IP pública del cliente
    fetch('https://api.ipify.org?format=json')
    .then(response => response.json())
    .then(data => {
        const clientIp = data.ip;  // Aquí tienes la IP del cliente

        // Obtener datos del localStorage o usar valores predeterminados
        const codigoPostal = localStorage.getItem('codigoPostal') || '12345';
        const latitude = localStorage.getItem('latitude') || '40.7128';
        const longitude = localStorage.getItem('longitude') || '-74.0060';
        const language = localStorage.getItem('language') || 'es';
        const usuario_id = localStorage.getItem('usuario_id') || 28;  // ID del usuario
        const correo_electronico = localStorage.getItem('correo_electronico') || 'usuario@example.com';

        // Datos que se enviarán
        const datosAcceso = {
            client_ip: clientIp,  // IP del cliente obtenida
            codigoPostal: codigoPostal,
            latitude: latitude,
            longitude: longitude,
            language: language,
            usuario_id: usuario_id,  // ID del usuario
            correo_electronico: correo_electronico
        };

        // Llama a la función para registrar el acceso
        registrarAcceso(datosAcceso);
    })
    .catch(error => {
        console.error('Error al obtener la IP:', error);
    });
}

// Función para registrar acceso (como en el ejemplo anterior)
function registrarAcceso(data) {
    debugger;
    fetch('/log_acceso/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Convierte el objeto `data` a JSON
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok') {
            console.log('Acceso registrado correctamente');
        } else {
            console.error('Hubo un problema al registrar el acceso');
        }
    })
    .catch(error => {
        console.error('Error al enviar la solicitud:', error);
    });
}

// Espera 10 segundos después de cargar la página
// Espera 10 segundos después de cargar la página
window.onload = function() {
    setTimeout(function() {
        // Ejecutar la función para obtener la IP y registrar el acceso
        obtenerIPYRegistrarAcceso();
    }, 10000); // Esperar 10 segundos antes de empezar el primer registro
};
