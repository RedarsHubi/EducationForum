document.addEventListener('DOMContentLoaded', function() {
  // Variables for the WebSocket and chat elements
  const chatWindow = document.getElementById('chat-window');
  const chatToggle = document.getElementById('toggle-chat');
  const chatMessages = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const sendChat = document.getElementById('send-chat');
  
  // Ensure the chat window is initially hidden
  chatWindow.style.display = 'none';

  // WebSocket connection
  let chatSocket;
  try {
      chatSocket = new WebSocket('wss://' + window.location.host + '/ws/chat/');
      console.log('WebSocket connection established');
  } catch (error) {
      console.error('WebSocket connection failed:', error);
      return;
  }

  // Toggle chat visibility
  chatToggle.addEventListener('click', function() {
      console.log('Chat toggle clicked');
      if (chatWindow.style.display === 'none') {
          chatWindow.style.display = 'block';
      } else {
          chatWindow.style.display = 'none';
      }
  });

  // WebSocket event handlers
  chatSocket.onmessage = function(event) {
      console.log('Received message:', event.data);
      const data = JSON.parse(event.data);
      const user = data.user;
      const message = data.message;

      // Add the received message to the chat window
      const newMessage = document.createElement('p');
      newMessage.innerHTML = `<strong>${user}:</strong> ${message}`;
      chatMessages.appendChild(newMessage);

      // Scroll chat messages to the bottom
      chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  chatSocket.onclose = function(event) {
      console.error('Chat socket closed unexpectedly');
  };

  // Sending a message
  const sendMessage = function() {
      const message = chatInput.value;
      if (message.trim() !== '') {
          console.log('Sending message:', message);
          chatSocket.send(JSON.stringify({
              'message': message
          }));
          chatInput.value = '';  // Clear input after sending
      }
  };

  sendChat.addEventListener('click', sendMessage);

  // Add event listener to chat input for the Enter key
  chatInput.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
          event.preventDefault();
          sendMessage();
      }
  });

  
});