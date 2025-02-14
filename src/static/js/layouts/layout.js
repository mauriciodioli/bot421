



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
        event.preventDefault(); // Evitar comportamiento por defecto del enlace
        const form = document.getElementById('ventas-form');
        // Asignar valores dinámicos al formulario (si es necesario)
        let access_token = localStorage.getItem("access_token")
    
        var ambito = localStorage.getItem("dominio");
        
        document.getElementById('access_token_form_Ventas').value = access_token;
        document.getElementById('ambito_form_Ventas').value = ambito;
        // Enviar el formulario
        form.submit();
    });

});


document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('compras-link').addEventListener('click', function (event) {
        event.preventDefault(); // Evitar comportamiento por defecto del enlace
        const form = document.getElementById('compras-form');
        // Asignar valores dinámicos al formulario (si es necesario)
        let access_token = localStorage.getItem("access_token")
    
        var ambito = localStorage.getItem("dominio");
        
        document.getElementById('access_token_btn_compras').value = access_token;
        document.getElementById('ambito_btn_compras').value = ambito;
        // Enviar el formulario
        form.submit();
    });

});


document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('consultas-link').addEventListener('click', function (event) {
     
        event.preventDefault(); // Evitar comportamiento por defecto del enlace
        const form = document.getElementById('consultas-form');
        // Asignar valores dinámicos al formulario (si es necesario)
        let access_token = localStorage.getItem("access_token")
    
        var ambito = localStorage.getItem("dominio");
        
        document.getElementById('access_token_btn_consultas').value = access_token;
        document.getElementById('ambito_btn_consultas').value = ambito;
        // Enviar el formulario
        form.submit();
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
  var languageLink = document.getElementById("languageLink");

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
    if (languageLink) {
        languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";
    } else {
        console.error("Element with ID 'yourElementId' not found.");
    }
    
}





function cambiarIdioma() {
    

document.addEventListener("DOMContentLoaded", function () {
     languageLink = document.getElementById("languageLink");

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

        if (languageLink) {
              // Actualizar el texto del enlace
             languageLink.textContent = currentLanguage === "in" ? "ENG" : "ES";

        } else {
            console.error("Element with ID 'yourElementId' not found.");
        }
      
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















document.addEventListener('DOMContentLoaded', function() {
    // Inicializamos el modal fuera del listener
    const modalElement = document.getElementById('modalSeleccionCodigoPostal');
    const myModal = new bootstrap.Modal(modalElement);

    // Obtener el enlace "Signals"
    document.getElementById('openModalCP').addEventListener('click', function (e) {
        // Prevenir el comportamiento por defecto (enlace)
        e.preventDefault();

        // Cargar el código postal desde el localStorage si existe
        const codigoPostalGuardado = localStorage.getItem('codigoPostal');
        const codigoPostalModal = document.getElementById('codigoPostalModal');
        if (codigoPostalGuardado) {
            // Mostrar el código postal guardado en el campo del modal
            codigoPostalModal.value = codigoPostalGuardado;
        } else {
            // Si no hay código postal en localStorage, dejar el campo vacío
            codigoPostalModal.value = '';
        }

        // Asegurarse de que solo se ingresen números
        codigoPostalModal.addEventListener('input', function(event) {
            // Reemplazar todo lo que no sea un número
            event.target.value = event.target.value.replace(/[^0-9]/g, '');
        });

        // Abrir el modal
        myModal.show();
    });
});
// Función para guardar el código postal en el localStorage y las cookies
function guardarCodigoPostal() {
    const codigoPostal = document.getElementById('codigoPostalModal').value;

    // Validar si el campo no está vacío y contiene solo números
    if (codigoPostal && !isNaN(codigoPostal)) {
        // Guardar el código postal en el localStorage
        localStorage.setItem('codigoPostal', codigoPostal);
        console.log('Código Postal guardado en localStorage:', codigoPostal);

        // Guardar el código postal en las cookies (con una duración de 1 hora)
        document.cookie = `codigoPostal=${codigoPostal};max-age=3600;path=/`;

        // Cerrar el modal
        const myModal = bootstrap.Modal.getInstance(document.getElementById('modalSeleccionCodigoPostal'));
        myModal.hide();  // Aquí se cierra el modal

    } else {
        alert('Por favor ingresa un código postal válido (solo números)');
    }
}

// Función para permitir solo números en el input
document.getElementById('codigoPostalModal').addEventListener('input', function(event) {
    // Reemplazar todo lo que no sea un número
    event.target.value = event.target.value.replace(/[^0-9]/g, '');
});































