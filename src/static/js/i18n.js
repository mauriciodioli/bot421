// i18n.js

const translations = {
    "es": {
        "ingresa_tus_datos": "Ingresa tus datos para recibir tu pedido!",
        "nombre": "Nombre",
        "apellido": "Apellido",
        "direccion": "Dirección",
        "telefono": "Teléfono",
        "email": "Email",
        "comentarios": "Comentarios",
        "datos_del_pedido": "Datos del pedido",
        "descuento": "Descuento",
        "continuar": "Continuar",
        "confirmar": "Confirmar",
        "metodo_pago": "Método de Pago",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Reservar Paquete",
        "reservar_cita": "Reservar Cita"
            },
    "in": {
        "ingresa_tus_datos": "Enter your details to receive your order!",
        "nombre": "First Name",
        "apellido": "Last Name",
        "direccion": "Address",
        "telefono": "Phone",
        "email": "Email",
        "comentarios": "Comments",
        "datos_del_pedido": "Order Details",
        "descuento": "Discount",
        "continuar": "Continue",
        "confirmar": "Confirm",
        "metodo_pago": "Payment Method",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Reserve Package",
        "reservar_cita": "Book Appointment"
    },
    "pt": {
        "ingresa_tus_datos": "Digite seus dados para receber seu pedido!",
        "nombre": "Nome",
        "apellido": "Sobrenome",
        "direccion": "Endereço",
        "telefono": "Telefone",
        "email": "E-mail",
        "comentarios": "Comentários",
        "datos_del_pedido": "Detalhes do pedido",
        "descuento": "Desconto",
        "continuar": "Continuar",
        "confirmar": "Confirmar",
        "metodo_pago": "Método de Pagamento",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Reservar Pacote",
        "reservar_cita": "Agendar Consulta"

    },
    "it": {
        "ingresa_tus_datos": "Inserisci i tuoi dati per ricevere il tuo ordine!",
        "nombre": "Nome",
        "apellido": "Cognome",
        "direccion": "Indirizzo",
        "telefono": "Telefono",
        "email": "Email",
        "comentarios": "Commenti",
        "datos_del_pedido": "Dettagli dell'ordine",
        "descuento": "Sconto",
        "continuar": "Continua",
        "confirmar": "Conferma",
        "metodo_pago": "Metodo di Pagamento",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Prenota Pacchetto",
        "reservar_cita": "Prenota Appuntamento"

    },
    "pl": {
        "ingresa_tus_datos": "Wprowadź swoje dane, aby otrzymać zamówienie!",
        "nombre": "Imię",
        "apellido": "Nazwisko",
        "direccion": "Adres",
        "telefono": "Telefon",
        "email": "Email",
        "comentarios": "Komentarze",
        "datos_del_pedido": "Szczegóły zamówienia",
        "descuento": "Zniżka",
        "continuar": "Kontynuuj",
        "confirmar": "Potwierdź",
        "metodo_pago": "Metoda Płatności",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Zarezerwuj Paczkę",
        "reservar_cita": "Zarezerwuj Wizytę"

    },
    "fr": {
        "ingresa_tus_datos": "Entrez vos informations pour recevoir votre commande!",
        "nombre": "Prénom",
        "apellido": "Nom",
        "direccion": "Adresse",
        "telefono": "Téléphone",
        "email": "Email",
        "comentarios": "Commentaires",
        "datos_del_pedido": "Détails de la commande",
        "descuento": "Remise",
        "continuar": "Continuer",
        "confirmar": "Confirmer",
        "metodo_pago": "Méthode de Paiement",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Réserver le Colis",
        "reservar_cita": "Réserver un Rendez-vous"

    },
    "de": {
        "ingresa_tus_datos": "Geben Sie Ihre Daten ein, um Ihre Bestellung zu erhalten!",
        "nombre": "Vorname",
        "apellido": "Nachname",
        "direccion": "Adresse",
        "telefono": "Telefon",
        "email": "E-Mail",
        "comentarios": "Kommentare",
        "datos_del_pedido": "Bestelldaten",
        "descuento": "Rabatt",
        "continuar": "Weiter",
        "confirmar": "Bestätigen",
        "metodo_pago": "Zahlungsmethode",
        "paypal": "PayPal",
        "mercado_pago": "Mercado Pago",
        "reservar_paquete": "Paket Reservieren",
        "reservar_cita": "Termin Vereinbaren"

    }
};




// Función para obtener el valor de una cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Función para aplicar las traducciones
function translate(lang) {
    const elements = document.querySelectorAll('[data-translate]');
    elements.forEach((el) => {
        const translationKey = el.getAttribute('data-translate');
        const translation = translations[lang] && translations[lang][translationKey];

        if (translation) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.setAttribute('placeholder', translation);
            } else {
                el.innerText = translation;
            }
        }
    });
}


// Detectar el idioma desde las cookies (si no existe, predeterminado a español)
debugger;
let currentLang = getCookie('language') 
               || localStorage.getItem('language') 
               || navigator.language?.split('-')[0]  // ej: 'en-US' → 'en'
               || 'es';  // idioma por defecto
if (currentLang === 'en') currentLang = 'in';
// Aplica las traducciones
translate(currentLang);