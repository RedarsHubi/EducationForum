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

  function connectWebSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      chatSocket = new WebSocket(protocol + '//' + window.location.host + '/ws/chat/');

      chatSocket.onopen = function(event) {
          console.log('WebSocket connection established');
      };

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
          // Attempt to reconnect after 5 seconds
          setTimeout(connectWebSocket, 5000);
      };

      chatSocket.onerror = function(error) {
          console.error('WebSocket error:', error);
      };
  }

  connectWebSocket();

  // Toggle chat visibility
  chatToggle.addEventListener('click', function() {
      console.log('Chat toggle clicked');
      chatWindow.style.display = chatWindow.style.display === 'none' ? 'block' : 'none';
  });

  // Sending a message
  function sendMessage() {
      const message = chatInput.value.trim();
      if (message !== '') {
          console.log('Sending message:', message);
          if (chatSocket.readyState === WebSocket.OPEN) {
              chatSocket.send(JSON.stringify({
                  'message': message
              }));
              chatInput.value = ''; // Clear input after sending
          } else {
              console.error('WebSocket is not open. ReadyState:', chatSocket.readyState);
          }
      }
  }

  sendChat.addEventListener('click', sendMessage);

  // Add event listener to chat input for the Enter key
  chatInput.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
          event.preventDefault();
          sendMessage();
      }
  });
});