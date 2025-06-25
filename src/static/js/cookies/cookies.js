document.addEventListener("DOMContentLoaded", function () {
    const messages = {
        "es": "Debes aceptar las cookies para continuar.",
        "en": "You must accept cookies to continue.",
        "fr": "Vous devez accepter les cookies pour continuer.",
        "de": "Sie müssen Cookies akzeptieren, um fortzufahren.",
        "it": "Devi accettare i cookie per continuare.",
        "pt": "Você deve aceitar os cookies para continuar."
    };

    // Detectar el idioma del usuario
    let userLang = navigator.language || navigator.userLanguage;
    userLang = userLang.split("-")[0]; // Solo tomar el código de idioma principal

    // Si el idioma no está en la lista, usar inglés como predeterminado
    let message = messages[userLang] || messages["en"];

    if (!localStorage.getItem("cookiesAccepted")) {
        document.getElementById("cookieConsent").style.display = "block";
    } else if (localStorage.getItem("cookiesAccepted") === "false") {
        document.body.innerHTML = `<h2>${message}</h2>`;
    }

    document.getElementById("acceptCookies").addEventListener("click", function () {
        localStorage.setItem("cookiesAccepted", "true");
        document.getElementById("cookieConsent").style.display = "none";
    });

    document.getElementById("rejectCookies").addEventListener("click", function () {
        localStorage.removeItem("cookiesAccepted");
        document.body.innerHTML = `<h2>${message}</h2>`;
    });
});
