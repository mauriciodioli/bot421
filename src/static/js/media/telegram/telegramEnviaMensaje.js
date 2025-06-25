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
                // Limpiar los campos del formulario
                $('#header').val('');
                $('#body').val('');
            },
            error: function(xhr, status, error) {
                alert('Error al enviar el mensaje');
            }
        });
    });
});
// Function to insert the selected emoticon into the textarea
function insertEmoticon(emoticon) {
    const bodyTextarea = document.getElementById('body');
    const cursorPosition = bodyTextarea.selectionStart;
    const textBefore = bodyTextarea.value.substring(0, cursorPosition);
    const textAfter = bodyTextarea.value.substring(cursorPosition);
    bodyTextarea.value = textBefore + emoticon + textAfter;
    bodyTextarea.focus();
    bodyTextarea.selectionStart = cursorPosition + emoticon.length;
    bodyTextarea.selectionEnd = cursorPosition + emoticon.length;

    // Close the modal
    const modalElement = document.getElementById('emoticonModal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalElement);
    modal.hide();
}

document.addEventListener('DOMContentLoaded', (event) => {
    const modal = document.getElementById('emoticonModal');
    if (modal) {
        modal.addEventListener('shown.bs.modal', loadEmoticons);
    } else {
        console.error('Modal element not found.');
    }
});

function toggleEmoticons() {
    const emoticonsDiv = document.getElementById('emoticonEmoticons');
    const isVisible = getComputedStyle(emoticonsDiv).display !== 'none';

    if (isVisible) {
        // Ocultar emoticonos si están visibles
        emoticonsDiv.style.display = 'none';
    } else {
        // Cargar emoticonos si están ocultos
        loadEmoticons();
        emoticonsDiv.style.display = 'block';
    }
}

function loadEmoticons() {
    fetch('/emoticons')
        .then(response => response.json())
        .then(data => {
            const emoticonsDiv = document.getElementById('emoticonEmoticons');
            emoticonsDiv.innerHTML = data.map(emoticon => 
                `<span class="emoticon" onclick="insertEmoticon('${emoticon}')">${emoticon}</span>`
            ).join(' ');
        })
        .catch(error => console.error('Error:', error));
}