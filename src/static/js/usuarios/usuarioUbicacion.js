let lastLatitude = null;
let lastLongitude = null;
let lastLanguage = null; // Para evitar enviar datos repetidos

// Función para obtener la ubicación
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(successCallback, errorCallback, {
            enableHighAccuracy: true, // Mayor precisión
            timeout: 10000, // 10 segundos para obtener ubicación
            maximumAge: 0 // No usar caché
        });
    } else {
        document.getElementById("status").innerText = "Geolocalización no soportada por este navegador.";
    }
}

// Éxito en la obtención de ubicación
function successCallback(position) {
    let latitude = position.coords.latitude;
    let longitude = position.coords.longitude;
    console.log(`📍 Ubicación obtenida: Latitud: ${latitude}, Longitud: ${longitude}`);
    document.getElementById("status").innerText = `Ubicación actual: Lat ${latitude}, Lng ${longitude}`;

    // Si la ubicación ha cambiado, obtener el idioma y enviarlo al servidor
    if (lastLatitude !== latitude || lastLongitude !== longitude) {
        lastLatitude = latitude;
        lastLongitude = longitude;
        getLanguageFromLocation(latitude, longitude);
    }
}

// Error al obtener ubicación
function errorCallback(error) {
    let message = "";
    switch (error.code) {
        case error.PERMISSION_DENIED:
            message = "Permiso denegado por el usuario.";
            break;
        case error.POSITION_UNAVAILABLE:
            message = "Ubicación no disponible.";
            break;
        case error.TIMEOUT:
            message = "Tiempo de espera agotado.";
            break;
        default:
            message = "Error desconocido.";
    }
    document.getElementById("status").innerText = message;
}

// Obtener idioma basado en la ubicación (usando OpenStreetMap Nominatim)
function getLanguageFromLocation(latitude, longitude) {
    let url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.address && data.address.country_code) {
                let countryCode = data.address.country_code.toUpperCase();
                let language = getLanguageByCountryCode(countryCode);
                console.log(`🌍 País detectado: ${data.address.country} (${countryCode}) - 🗣 Idioma: ${language}`);
                document.getElementById("status").innerText = `Ubicación detectada: ${data.address.country} - Idioma: ${language}`;

                // Solo enviar si el idioma ha cambiado
                if (lastLanguage !== language) {
                    lastLanguage = language;
                    sendLocationToServer(latitude, longitude, language);
                }
            }
        })
        .catch(error => console.error("Error obteniendo detalles de la ubicación:", error));
}

// Mapa de códigos de país a idioma principal
function getLanguageByCountryCode(countryCode) {
    const languageMap = {
        "EN": ["US", "GB", "AU", "CA", "NZ"], // Inglés
        "ES": ["ES", "MX", "AR", "CO", "PE", "CL", "VE", "EC", "BO", "PY", "UY", "DO", "CU"], // Español
        "FR": ["FR", "BE", "CH", "CA"], // Francés
        "DE": ["DE", "AT", "CH", "LI"], // Alemán
        "IT": ["IT", "SM", "VA"], // Italiano
        "PT": ["PT", "BR", "AO", "MZ"], // Portugués
        "RU": ["RU", "BY", "KZ"], // Ruso
        "CN": ["CN", "SG"], // Chino
        "JA": ["JP"], // Japonés
        "HI": ["IN"], // Hindi
        "AR": ["SA", "AE", "EG", "DZ", "MA"], // Árabe
    };

    // Buscar el idioma por código de país
    for (const [language, countries] of Object.entries(languageMap)) {
        if (countries.includes(countryCode.toUpperCase())) {
            return getLanguageName(language);
        }
    }

    return "Unknown";
}

// Función auxiliar para convertir códigos de idioma a nombres en inglés
function getLanguageName(code) {
    const languageNames = {
        "EN": "English",
        "ES": "Spanish",
        "FR": "French",
        "DE": "German",
        "IT": "Italian",
        "PT": "Portuguese",
        "RU": "Russian",
        "CN": "Chinese",
        "JA": "Japanese",
        "HI": "Hindi",
        "AR": "Arabic"
    };

    return languageNames[code] || "Unknown";
}

// Enviar la ubicación y el idioma al servidor con AJAX
// Función para establecer una cookie con expiración
function setCookie(name, value, days) {
    let expires = "";
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + encodeURIComponent(value) + expires + "; path=/";
}

// Función para obtener una cookie
function getCookie(name) {
    let nameEQ = name + "=";
    let cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        let cookie = cookies[i].trim();
        if (cookie.indexOf(nameEQ) === 0) {
            return decodeURIComponent(cookie.substring(nameEQ.length));
        }
    }
    return null;
}

// Enviar la ubicación y el idioma al servidor con AJAX
function sendLocationToServer(latitude, longitude, language) {
    if (language && typeof language === "string") { // Verifica que sea un string válido
        try {
            // Guardar en localStorage
            localStorage.setItem("language", language);
            console.log("Idioma guardado en localStorage:", language);
            
            // Guardar en cookies por 30 días
            setCookie("language", language, 30);
            console.log("Idioma guardado en cookies:", language);
            
        } catch (error) {
            console.error("Error guardando en localStorage o cookies:", error);
        }
    }

    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/usuarios-usuarioUbicacion-update-location/", true);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                console.log("Ubicación e idioma actualizados en el servidor:", xhr.responseText);
            } else {
                console.error("Error en la actualización:", xhr.status, xhr.responseText);
            }
        }
    };

    let data = JSON.stringify({ 
        latitude: latitude, 
        longitude: longitude,
        language: language 
    });
    xhr.send(data);
}

// Recuperar el idioma guardado (opcional)
function getSavedLanguage() {
    return localStorage.getItem("language") || getCookie("language") || "Unknown";
}



// Llamar a getLocation cada 10 segundos para verificar cambios
setInterval(getLocation, 3600000); // 3600000 ms = 1 hora

