<<<<<<< HEAD
$(document).ready(function() {
    // Evento para enviar el formulario de restablecimiento de contraseña
    $("#password-reset-form").on("submit", function(e) {
        e.preventDefault();
        let email = $("#email").val();
        localStorage.setItem('correo_electronico', email);
        $.ajax({
            url: "/send_reset_email",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email }),
            success: function(response) {
                alert('SE ENVIO CODIGO DE RECUPERACION DE CONTRASEÑA, REVISE SU CORREO');
                $("#password-reset-form").hide();
                $("#verification-form").show();
                
                // Iniciar el contador descendente de 2 minutos
                startCountdown();
            },
            error: function(error) {
                alert("Error al enviar el correo de recuperación.");
            }
        });
    });

    // Función para iniciar el contador descendente
    function startCountdown() {
        let duration = 120; // Duración en segundos (2 minutos)
        let countdownElement = $("#countdown");
        
        // Actualizar el contador cada segundo
        let countdownInterval = setInterval(function() {
            let minutes = Math.floor(duration / 60);
            let seconds = duration % 60;
            
            // Formatear el tiempo restante como MM:SS
            let countdownText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            countdownElement.text(countdownText);
            
            // Reducir el tiempo restante
            duration--;
            
            // Detener el contador cuando llegue a cero
            if (duration < 0) {
                clearInterval(countdownInterval);
                countdownElement.text("Tiempo expirado");
            }
        }, 1000); // Intervalo de 1 segundo
    }

    // Evento para verificar el código de verificación
    $("#verify-code-btn").on("click", function(e) {
        e.preventDefault();
        let verificationCode = '';
        $('.code-inputs input').each(function() {
            verificationCode += $(this).val();
        });

        $.ajax({
            url: "/verify_code",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ verification_code: verificationCode }),
            success: function(response) {
                alert('CODIGO CORRECTO, INGRESE NUEVA CONTRASEÑA');
                $("#verification-form").hide();
                $("#new-password-form").show();
            },
            error: function(error) {
                alert("Código de verificación incorrecto.");
            }
        });
    });

    // Evento para enviar el formulario de nueva contraseña y validar coincidencia
    $("#new-password-form").on("submit", function(e) {
        e.preventDefault();
        let newPassword = $("#new-password").val();
        let confirmPassword = $("#confirm-password").val();
        let correo_electronico = localStorage.getItem("correo_electronico");

        if (newPassword !== confirmPassword) {
            alert("Las contraseñas no coinciden. Por favor, inténtelo de nuevo.");
            return; // Evita que el formulario se envíe
        }

        $.ajax({
            url: "/reset_password",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                new_password: newPassword,
                correo_electronico: correo_electronico
            }),
            success: function(response) {
                alert(response.message);
                window.location.href = "/index#ingreso"; // Redirigir a /index#ingreso
            },
            error: function(error) {
                alert(error.responseJSON.error); // Mostrar el mensaje de error del servidor
            }
        });
    });
});

// Función para mover el foco al siguiente campo de entrada
function moveToNext(current, nextFieldID) {
    if (current.value.length == current.maxLength) {
        document.getElementById(nextFieldID).focus();
    }
}

// Función para alternar la visibilidad de la contraseña
function togglePasswordVisibility(id) {
    var passwordField = document.getElementById(id);
    var icon = passwordField.nextElementSibling.querySelector('.toggle-password');

    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.textContent = "🙈";
    } else {
        passwordField.type = "password";
        icon.textContent = "👁️";
    }
}
=======
$(document).ready(function() {
    // Evento para enviar el formulario de restablecimiento de contraseña
    $("#password-reset-form").on("submit", function(e) {
        e.preventDefault();
        let email = $("#email").val();
        localStorage.setItem('correo_electronico', email);
        $.ajax({
            url: "/send_reset_email",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ email: email }),
            success: function(response) {
                alert('SE ENVIO CODIGO DE RECUPERACION DE CONTRASEÑA, REVISE SU CORREO');
                $("#password-reset-form").hide();
                $("#verification-form").show();
                
                // Iniciar el contador descendente de 2 minutos
                startCountdown();
            },
            error: function(error) {
                alert("Error al enviar el correo de recuperación.");
            }
        });
    });

    // Función para iniciar el contador descendente
    function startCountdown() {
        let duration = 120; // Duración en segundos (2 minutos)
        let countdownElement = $("#countdown");
        
        // Actualizar el contador cada segundo
        let countdownInterval = setInterval(function() {
            let minutes = Math.floor(duration / 60);
            let seconds = duration % 60;
            
            // Formatear el tiempo restante como MM:SS
            let countdownText = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            countdownElement.text(countdownText);
            
            // Reducir el tiempo restante
            duration--;
            
            // Detener el contador cuando llegue a cero
            if (duration < 0) {
                clearInterval(countdownInterval);
                countdownElement.text("Tiempo expirado");
            }
        }, 1000); // Intervalo de 1 segundo
    }

    // Evento para verificar el código de verificación
    $("#verify-code-btn").on("click", function(e) {
        e.preventDefault();
        let verificationCode = '';
        $('.code-inputs input').each(function() {
            verificationCode += $(this).val();
        });

        $.ajax({
            url: "/verify_code",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ verification_code: verificationCode }),
            success: function(response) {
                alert('CODIGO CORRECTO, INGRESE NUEVA CONTRASEÑA');
                $("#verification-form").hide();
                $("#new-password-form").show();
            },
            error: function(error) {
                alert("Código de verificación incorrecto.");
            }
        });
    });

    // Evento para enviar el formulario de nueva contraseña y validar coincidencia
    $("#new-password-form").on("submit", function(e) {
        e.preventDefault();
        let newPassword = $("#new-password").val();
        let confirmPassword = $("#confirm-password").val();
        let correo_electronico = localStorage.getItem("correo_electronico");

        if (newPassword !== confirmPassword) {
            alert("Las contraseñas no coinciden. Por favor, inténtelo de nuevo.");
            return; // Evita que el formulario se envíe
        }

        $.ajax({
            url: "/reset_password",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                new_password: newPassword,
                correo_electronico: correo_electronico
            }),
            success: function(response) {
                alert(response.message);
                window.location.href = "/index#ingreso"; // Redirigir a /index#ingreso
            },
            error: function(error) {
                alert(error.responseJSON.error); // Mostrar el mensaje de error del servidor
            }
        });
    });
});

// Función para mover el foco al siguiente campo de entrada
function moveToNext(current, nextFieldID) {
    if (current.value.length == current.maxLength) {
        document.getElementById(nextFieldID).focus();
    }
}

// Función para alternar la visibilidad de la contraseña
function togglePasswordVisibility(id) {
    var passwordField = document.getElementById(id);
    var icon = passwordField.nextElementSibling.querySelector('.toggle-password');

    if (passwordField.type === "password") {
        passwordField.type = "text";
        icon.textContent = "🙈";
    } else {
        passwordField.type = "password";
        icon.textContent = "👁️";
    }
}
>>>>>>> c771be39e03a9cc8cb8ab015daa471515565c719
