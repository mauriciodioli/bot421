// Función para obtener la IP del cliente y registrar el acceso
function obtenerIPYRegistrarAcceso() {
    // Lista de IPs maliciosas conocidas (puedes agregar más IPs a esta lista)
    const ipsMaliciosas = [
        "205.169.39.57", // IP reportada como maliciosa
        "34.123.170.104", // Otra IP reportada
        // Puedes agregar más IPs maliciosas aquí
    ];
    debugger;
    // Utiliza ipify para obtener la IP pública del cliente
    fetch('https://api.ipify.org?format=json')
    .then(response => response.json())
    .then(data => {
        const clientIp = data.ip;  // Aquí tienes la IP del cliente

        // Verificar si la IP del cliente está en la lista de IPs maliciosas
        if (ipsMaliciosas.includes(clientIp)) {
            console.log(`Acceso bloqueado para la IP: ${clientIp}`);
            // Si la IP está en la lista, rechazar el acceso y mostrar un mensaje
            alert('Acceso bloqueado desde esta IP.');
            return;  // Detener el proceso aquí si la IP está bloqueada
        }

        // Obtener datos del localStorage o usar valores predeterminados
        const codigoPostal = localStorage.getItem('codigoPostal') || '12345';
        let latitude = localStorage.getItem('latitude');
        let longitude = localStorage.getItem('longitude');
        const language = localStorage.getItem('language') || 'es';
        const usuario_id = localStorage.getItem('usuario_id') || 28;  // ID del usuario
        const correo_electronico = localStorage.getItem('correo_electronico') || 'usuario@example.com';

        // Si no hay latitud y longitud en el localStorage, obtenerlas desde la IP
        if (!latitude || !longitude) {
            // Usar una API de geolocalización para obtener la latitud y longitud de la IP
            fetch(`https://ipinfo.io/${clientIp}/json`)
            .then(response => response.json())
            .then(locationData => {
                // Si la respuesta tiene los datos de la ubicación, extraemos la latitud y longitud
                const location = locationData.loc ? locationData.loc.split(',') : ['40.7128', '-74.0060'];  // Si no se puede obtener, usa un valor predeterminado
                latitude = location[0];
                longitude = location[1];

                // Guardar la ubicación en el localStorage para futuras consultas
                localStorage.setItem('latitude', latitude);
                localStorage.setItem('longitude', longitude);

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
                console.error('Error al obtener la ubicación:', error);
                // Si hay un error al obtener la ubicación, se usan valores predeterminados
                latitude = '40.7128';
                longitude = '-74.0060';
                
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
            });
        } else {
            // Si ya hay latitud y longitud, solo registramos los datos
            const datosAcceso = {
                client_ip: clientIp,
                codigoPostal: codigoPostal,
                latitude: latitude,
                longitude: longitude,
                language: language,
                usuario_id: usuario_id,  // ID del usuario
                correo_electronico: correo_electronico
            };

            // Llama a la función para registrar el acceso
            registrarAcceso(datosAcceso);
        }
    })
    .catch(error => {
        console.error('Error al obtener la IP:', error);
    });
}


// Función para registrar acceso (como en el ejemplo anterior)
function registrarAcceso(data) {
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
