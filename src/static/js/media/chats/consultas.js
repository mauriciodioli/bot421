document.getElementById('openChat').addEventListener('click', function() {
    const chatWidget = document.getElementById('chatWidget');
    chatWidget.style.display = chatWidget.style.display === 'none' ? 'block' : 'none';
});

document.getElementById('closeChat').addEventListener('click', function() {
    document.getElementById('chatWidget').style.display = 'none';
});
  
  
  // Function to create new chat windows dynamically
        function createChatWindow(userId) {
            // Create chat window elements
            let chatWindow = document.createElement('div');
            chatWindow.classList.add('chat-popup');
            chatWindow.id = 'chat-window-' + userId;

            let chatHeader = document.createElement('div');
            chatHeader.classList.add('chat-header');
            chatHeader.innerText = 'Chat with User ' + userId;

            let chatBody = document.createElement('div');
            chatBody.classList.add('chat-body');

            let chatFooter = document.createElement('div');
            chatFooter.classList.add('chat-footer');
            let input = document.createElement('input');
            input.type = 'text';
            input.placeholder = 'Escribe tu mensaje...';

            let sendButton = document.createElement('button');
            sendButton.innerText = 'Enviar';
            sendButton.onclick = function () {
                sendMessage(userId, input.value);
                input.value = '';  // Clear the input after sending
            };

            chatFooter.appendChild(input);
            chatFooter.appendChild(sendButton);

            chatWindow.appendChild(chatHeader);
            chatWindow.appendChild(chatBody);
            chatWindow.appendChild(chatFooter);

            document.getElementById('chat-container').appendChild(chatWindow);

            // Display the chat window
            chatWindow.style.display = 'block';
        }

        // Function to send message to server
        function sendMessage(userId, message) {
            fetch('/send_message/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: userId, message: message })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Message sent:', data);
            });
        }

        // Example of how to dynamically create a new chat window for a new user
        createChatWindow(1);  // This would be triggered when a new chat is initiated

        function pollForMessages() {
            setInterval(function() {
                fetch('/check_new_messages/')  // Endpoint que verifica mensajes nuevos
                    .then(response => response.json())
                    .then(data => {
                        if (data.newMessages) {
                            data.messages.forEach(msg => {
                                // Verifica si la ventana ya está creada antes de añadir un nuevo mensaje
                                createChatWindow(msg.userId);
                                updateChat(msg.text, 'user');  // Asegúrate de que la función updateChat esté bien definida
                            });
                        }
                    });
            }, 5000);  // Polling cada 5 segundos
        }
        function updateChat(message, sender) {
            let chatBody = document.getElementById('chatBody');
            let newMessage = document.createElement('div');
            newMessage.innerText = message;
        
            if (sender === 'user') {
                newMessage.classList.add('user-message');  // Aplica la clase para el usuario
            } else {
                newMessage.classList.add('admin-message');  // Aplica la clase para el administrador
            }
        
            chatBody.appendChild(newMessage);
            chatBody.scrollTop = chatBody.scrollHeight;  // Para que siempre esté al final del chat
        }
                