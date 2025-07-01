document.addEventListener('DOMContentLoaded', cargarPaises);

async function cargarPaises() {
    try {
        const response = await fetch('https://countriesnow.space/api/v0.1/countries/info?returns=name,unicodeFlag,dialCode');
        const data = await response.json();
        
        if (!data.error && data.data) {
            const paises = data.data;
            const selectPais = document.getElementById('pais');
            window.paisesData = {}; 

            // Ordenar países alfabéticamente
            paises.sort((a, b) => a.name.localeCompare(b.name));

            paises.forEach(pais => {
                const option = document.createElement('option');
                option.value = pais.name; // CountriesNow usa el nombre como identificador
                option.textContent = `${pais.unicodeFlag || ''} ${pais.name}`.trim(); 
                selectPais.appendChild(option);

                // Almacenar datos del país para uso posterior
                window.paisesData[pais.name] = {
                    nombre: pais.name,
                    bandera: pais.unicodeFlag,
                    codigoTelefono: pais.dialCode
                };
            });

            // Cargar idiomas para todos los países
            await cargarIdiomasPaises();
        }
    } catch (error) {
        console.error('Error al cargar los países:', error);
        // Fallback en caso de error
        mostrarErrorCargaPaises();
    }
}

async function cargarIdiomasPaises() {
    try {
        // CountriesNow tiene un endpoint específico para idiomas
        const response = await fetch('https://countriesnow.space/api/v0.1/countries/languages');
        const data = await response.json();
        
        if (!data.error && data.data) {
            data.data.forEach(paisIdioma => {
                if (window.paisesData[paisIdioma.country]) {
                    window.paisesData[paisIdioma.country].idiomas = paisIdioma.languages;
                }
            });
        }
    } catch (error) {
        console.error('Error al cargar idiomas:', error);
        // Agregar idiomas por defecto si falla
        Object.keys(window.paisesData).forEach(pais => {
            if (!window.paisesData[pais].idiomas) {
                window.paisesData[pais].idiomas = ['English']; // Idioma por defecto
            }
        });
    }
}

function mostrarErrorCargaPaises() {
    const selectPais = document.getElementById('pais');
    const option = document.createElement('option');
    option.value = '';
    option.textContent = 'Error al cargar países. Intente más tarde.';
    selectPais.appendChild(option);
}

function seleccionarIdioma() {
    const paisNombre = document.getElementById('pais').value;
    const datosPais = window.paisesData[paisNombre];
    const selectLenguaje = document.getElementById('lenguaje');
    
    selectLenguaje.innerHTML = '<option value="">--Seleccionar--</option>';

    if (datosPais && datosPais.idiomas) {
        datosPais.idiomas.forEach(idioma => {
            const option = document.createElement('option');
            option.value = idioma;
            option.textContent = idioma;
            selectLenguaje.appendChild(option);
        });
    } else {
        // Si no hay idiomas disponibles, agregar inglés como opción
        const option = document.createElement('option');
        option.value = 'English';
        option.textContent = 'English';
        selectLenguaje.appendChild(option);
    }

    // Actualizar etiquetas
    document.querySelector('label[for="pais"]').textContent = `País seleccionado: ${datosPais.nombre}`;
    document.querySelector('label[for="lenguaje"]').textContent = 'Selecciona tu idioma:';

    // Pasar a la siguiente sección
    mostrarSiguiente('seleccionPais', 'seleccionLenguaje');
}

function mostrarCodigoPostal() {
    const selectLenguaje = document.getElementById('lenguaje');
    if (selectLenguaje.value) {
        mostrarSiguiente('seleccionLenguaje', 'seleccionCodigoPostal');
    }
}

function mostrarSiguiente(actual, siguiente) {
    document.getElementById(actual).style.display = 'none';
    document.getElementById(siguiente).style.display = 'block';
}

async function enviarDatos() {
    const correo_electronico = document.getElementById('correo_electronico').value;
    const password = document.getElementById('password').value;
    const region = "region";
    const provincia = "provincia";
    const ciudad = "ciudad";
    
    try {
        const { latitude, longitude } = await obtenerUbicacion();
        console.log("Ubicación obtenida en registrarUsuarioRegion.js:", latitude, longitude);

        const datos = {
            pais: document.getElementById('pais').value,
            lenguaje: document.getElementById('lenguaje').value,
            codigoPostal: document.getElementById('codigoPostal').value,
            correo_electronico: correo_electronico,
            password: password,
            region: region,
            provincia: provincia,
            ciudad: ciudad,
            latitud: latitude,
            longitud: longitude
        };

        const response = await fetch('/registro-usuario/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(datos)
        });

        const html = await response.text();
        document.open();
        document.write(html);
        document.close();
    } catch (error) {
        console.error('Error al enviar los datos:', error);
    }
}

function obtenerUbicacion() {
    return new Promise((resolve, reject) => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                position => resolve({
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                }),
                error => reject(error),
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            reject(new Error("Geolocalización no soportada por este navegador."));
        }
    });
}
