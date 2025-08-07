



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
        console.error("Element with ID 'languageLink' not found.");
    }
    
}





document.addEventListener("DOMContentLoaded", function () {
    const selector = document.getElementById("languageSelector");
    const selected = selector.querySelector(".selected-language");
    const dropdown = selector.querySelector(".language-dropdown");
    const languageLink = document.getElementById("languageLink");

    const languages = {
        in: { name: "English", code: "ENG", flag: "https://flagcdn.com/24x18/us.png" },
        pl: { name: "Poland", code: "PL", flag: "https://flagcdn.com/24x18/pl.png" },       
        fr: { name: "Français", code: "FR", flag: "https://flagcdn.com/24x18/fr.png" },
        es: { name: "Español", code: "ES", flag: "https://flagcdn.com/24x18/es.png" },
        de: { name: "Deutsch", code: "DE", flag: "https://flagcdn.com/24x18/de.png" },
        it: { name: "Italiano", code: "IT", flag: "https://flagcdn.com/24x18/it.png" },
        pt: { name: "Português", code: "PT", flag: "https://flagcdn.com/24x18/pt.png" }
       
    };

    const availableLanguages = Object.keys(languages);

    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? match[2] : null;
    }

    function setLanguage(lang) {
        const langData = languages[lang];
        if (!langData) return;

        // Guardar
        localStorage.setItem("language", lang);
        document.cookie = `language=${lang}; path=/; max-age=31536000`;

        // Mostrar en selector visual
        selected.innerHTML = `<img src="${langData.flag}"> ${langData.code}`;

        // Mostrar en <a id="languageLink">
        if (languageLink) {
            languageLink.textContent = langData.code;
        }

        // Cerrar dropdown
        dropdown.style.display = "none";

        // Funciones del sistema
        if (typeof cargarAmbitos === "function") cargarAmbitos();
        if (typeof cargarAmbitosCarrusel === "function") cargarAmbitosCarrusel();
    }

    function buildDropdown() {
        dropdown.innerHTML = "";
        for (const [code, lang] of Object.entries(languages)) {
            const option = document.createElement("div");
            option.className = "language-option";
            option.innerHTML = `<img src="${lang.flag}"> ${lang.name}`;
            option.addEventListener("click", () => setLanguage(code));
            dropdown.appendChild(option);
        }
    }

    selected.addEventListener("click", () => {
        dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
        if (!selector.contains(e.target) && e.target !== languageLink) {
            dropdown.style.display = "none";
        }
    });

    // Clic sobre <a id="languageLink"> para cambiar idioma cíclicamente
    if (languageLink) {
        languageLink.addEventListener("click", function (event) {
            event.preventDefault();

            const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
            const currentIndex = availableLanguages.indexOf(currentLang);
            const nextIndex = (currentIndex + 1) % availableLanguages.length;
            const nextLang = availableLanguages[nextIndex];

            setLanguage(nextLang);
        });
    }

    // Inicializar
    const currentLang = localStorage.getItem("language") || getCookie("language") || "in";
    setLanguage(currentLang);
    buildDropdown();
});















 
 function cargaCodigoPostalLayout(){
    // Obtener referencia al label
    const labelCP = document.getElementById("labelCP");

    // Obtener el valor almacenado en localStorage
    const cpValue = localStorage.getItem("codigoPostal");

    // Si hay un valor en localStorage, asignarlo al label
    if (cpValue) {
        labelCP.textContent = cpValue;
    }
 

 }
 



document.addEventListener('DOMContentLoaded', function() {
    cargaCodigoPostalLayout();
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

  
        // Abrir el modal
        myModal.show();
    });
});
// Función para guardar el código postal en el localStorage y las cookies
function guardarCodigoPostal() {
    const codigoPostal = document.getElementById('codigoPostalModal').value;

    // Validar si el campo no está vacío y contiene solo números
   // if (codigoPostal) {
        // Guardar el código postal en el localStorage
        localStorage.setItem('codigoPostal', codigoPostal);
        document.cookie = `codigoPostal=${codigoPostal}; max-age=3600; path=/; SameSite=Lax`;
        console.log("Cookies accesibles por JS después de setear:", document.cookie);
        cargaCodigoPostalLayout();
        // Cerrar el modal
        const myModal = bootstrap.Modal.getInstance(document.getElementById('modalSeleccionCodigoPostal'));
        myModal.hide();  // Aquí se cierra el modal

 //   } else {
 //       alert('Por favor ingresa un código postal válido (solo números)');
  //  }
}
































