$(document).ready(function() {
    $('#telegramForm').on('submit', function(event) {
        event.preventDefault(); // Evita el envío del formulario por defecto

        const header = $('#header').val();
        const body = $('#body').val();

        const message = `${header}\n\n${body}`;
        const access_token = localStorage.getItem('access_token');
        
        const data = {
            access_token: access_token,           
            message: message
        };

        $.ajax({
            url: '/telegram-envia-mensaje-grupo', // URL de tu endpoint para enviar mensajes
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                alert('Mensaje enviado con éxito');
            },
            error: function(xhr, status, error) {
                alert('Error al enviar el mensaje');
            }
        });
    });
});