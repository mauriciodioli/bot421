// Definir la función que manejará el clic en "Administración"
function handleAdminClick(event) {
    event.preventDefault(); // Evita el comportamiento predeterminado del enlace
    
    const token = localStorage.getItem('access_token');
    if (!token) {
        alert('No se encontró un token de acceso.');
        return;
    }

    fetch('/herramientaAdmin-administracion', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            layout: 'layout_administracion',
            tipoUso: 'admin'
        })
    })
    .then(response => {
        if (response.ok) {
            return response.text(); // Recibe el HTML de la respuesta
        } else {
            throw new Error('Error en la solicitud');
        }
    })
    .then(html => {
        document.body.innerHTML = html; // Reemplaza el contenido actual por el nuevo HTML
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Ocurrió un error al procesar la solicitud.');
    });
}

// Asociar la función al enlace después de que el DOM esté cargado
document.addEventListener('DOMContentLoaded', function () {
    const adminLink = document.getElementById('admin-link');
    if (adminLink) {
        adminLink.addEventListener('click', handleAdminClick);
    } else {
        console.error("No se encontró el elemento con ID 'admin-link'.");
    }
});



document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('ventas-link').addEventListener('click', function (event) {
        event.preventDefault(); // Prevenir la acción predeterminada del enlace
        
        try {
            const token = localStorage.getItem('access_token');
            const dominio = localStorage.getItem('ambito');

            if (!token || !dominio) {
                throw new Error("Datos faltantes en localStorage.");
            }

            // Asignar valores al formulario
            document.getElementById('pedidos_ventas_accessToken').value = token;
            document.getElementById('pedidos_ventas_dominio').value = dominio;

            // Enviar el formulario
            document.getElementById('ventas-form').submit();
        } catch (error) {
            console.error("Error al procesar el formulario:", error.message);
            alert("No se pudo procesar la solicitud. Intente nuevamente.");
        }
    });
});





















































// Función para obtener el valor de una cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}


var currentLanguage = 'in';

// Obtener el enlace para cambiar el idioma
const languageLink = document.getElementById("languageLink");

// Si no existe la cookie "language", se crea y se establece "in" como idioma
if (!getCookie("language")) {
    document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`; // Validez de 1 año
    currentLanguage = "in";
    localStorage.setItem("language", currentLanguage);
    // Cambiar el texto del enlace según el idioma
    languageLink.textContent = "ENG";  // Cambiar solo a "ENG"
} else {
    // Si ya existe la cookie, obtener el valor y poner el texto de acuerdo a ella
    currentLanguage = getCookie("language");
    localStorage.setItem("language", currentLanguage);
    languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
}





function cambiarIdioma() {
    

document.addEventListener("DOMContentLoaded", function () {
    const languageLink = document.getElementById("languageLink");

    // Función para obtener el valor de una cookie
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    // Función para actualizar el idioma y mostrarlo
    function updateLanguage() {
        // Leer el idioma desde localStorage o cookies
        let currentLanguage = localStorage.getItem("language") || getCookie("language");

        // Si no hay un idioma configurado, asignar "in" como valor inicial
        if (!currentLanguage) {
            currentLanguage = "in";
        } else {
            // Alternar entre "in" y "es"
            currentLanguage = currentLanguage === "in" ? "es" : "in";
        }

        // Guardar el idioma actualizado en localStorage y cookies
        localStorage.setItem("language", currentLanguage);
        document.cookie = `language=${currentLanguage}; path=/; max-age=31536000`; // Validez de 1 año

        // Actualizar el texto del enlace
        languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";

        alert(`Idioma actualizado: ${currentLanguage}`);
    }

    // Establecer el idioma inicial y el texto del enlace
    (function setInitialLanguage() {
        const currentLanguage = localStorage.getItem("language") || getCookie("language") || "in";
        languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
    })();

    // Agregar el evento para alternar el idioma
    languageLink.addEventListener("click", function (event) {
        event.preventDefault(); // Evitar la recarga de la página
        updateLanguage();
    });
});

}













