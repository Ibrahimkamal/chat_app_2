const socket = io();
const messages = document.getElementById('messages');
const messageInput = document.getElementById('message');

// Join a room when connecting
socket.on('connect', () => {
    socket.emit('join', {room: 'general'});
});

// Handle receiving messages
socket.on('receive_message', (data) => {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${data.sender === getUserId() ? 'sent' : 'received'}`;
    messageDiv.textContent = data.message;
    messages.appendChild(messageDiv);
    messages.scrollTop = messages.scrollHeight;
});

function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        socket.emit('send_message', {
            message: message,
            room: 'general'
        });
        messageInput.value = '';
    }
}

function getUserId() {
    // This should be replaced with actual user ID from session
    return 'current_user';
}

// Handle enter key
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
}); 