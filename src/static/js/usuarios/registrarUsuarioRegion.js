document.addEventListener('DOMContentLoaded', cargarPaises);

async function cargarPaises() {
    try {
        const response = await fetch('https://restcountries.com/v3.1/all');
        const paises = await response.json();
        const selectPais = document.getElementById('pais');
        window.paisesData = {}; 

        paises.sort((a, b) => a.name.common.localeCompare(b.name.common));

        paises.forEach(pais => {
            const option = document.createElement('option');
            option.value = pais.cca2; 
            option.textContent = pais.name.common; 
            selectPais.appendChild(option);

            window.paisesData[pais.cca2] = {
                nombre: pais.name.common,
                idiomas: Object.values(pais.languages || {})
            };
        });
    } catch (error) {
        console.error('Error al cargar los países:', error);
    }
}

function seleccionarIdioma() {
    const paisCodigo = document.getElementById('pais').value;
    const datosPais = window.paisesData[paisCodigo];
    const selectLenguaje = document.getElementById('lenguaje');
    
    selectLenguaje.innerHTML = '<option value="">--Seleccionar--</option>';

    if (datosPais) {
        datosPais.idiomas.forEach(idioma => {
            const option = document.createElement('option');
            option.value = idioma;
            option.textContent = idioma;
            selectLenguaje.appendChild(option);
        });
    }

    // Actualizar etiquetas
    document.querySelector('label[for="pais"]').textContent = `País seleccionado: ${window.paisesData[paisCodigo].nombre}`;
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
