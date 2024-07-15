$(document).ready(function() {
    $("#password-reset-form").on("submit", function(e) {
        e.preventDefault();
        let email = $("#email").val();
        
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
        let verificationCode = $("#verification-code").val();

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

    // Evento para enviar el formulario de nueva contraseña
    $("#new-password-form").on("submit", function(e) {
        e.preventDefault();
        let newPassword = $("#new-password").val();

        $.ajax({
            url: "/reset_password",
            type: "POST",
            contentType: "application/json",
            data: JSON.stringify({ new_password: newPassword }),
            success: function(response) {
                alert(response.message);
            },
            error: function(error) {
                alert("Error al cambiar la contraseña.");
            }
        });
    });
});

// Validación de coincidencia de contraseñas
document.getElementById("new-password-form").addEventListener("submit", function(event) {
    var newPassword = document.getElementById("new-password").value;
    var confirmPassword = document.getElementById("confirm-password").value;

    if (newPassword !== confirmPassword) {
        alert("Las contraseñas no coinciden. Por favor, inténtelo de nuevo.");
        event.preventDefault(); // Evita que el formulario se envíe
    }
});