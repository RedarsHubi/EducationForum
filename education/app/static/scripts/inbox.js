let webSocket;

function initWebSocketConnection() {
    // Establish a WebSocket connection
    webSocket = new WebSocket('ws://' + window.location.host + '/ws/inbox/');

    webSocket.onopen = () => {
        console.log('WebSocket connection opened');
    };

    webSocket.onmessage = (event) => {
        console.log("Received WebSocket message:", event.data);
        const data = JSON.parse(event.data);
        if (data.type === 'unread_count_update') {
            console.log("Unread count update:", data.unread_count);
            updateUnreadCountBadge(data.unread_count);
        } else if (data.type === 'new_message') {
            console.log("New message received:", data);
            updateUnreadCountBadge(data.unread_count);
            animateNewMessages();
        }
    };

    webSocket.onclose = () => {
        console.log('WebSocket connection closed');
        // Reconnect or handle the disconnection
    };

    webSocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Handle the error
    };
}

function markConversationAsRead(senderId) {
    // Get all unread messages within the conversation
    const unreadMessages = document.querySelectorAll(`.conversation-card[onclick="markConversationAsRead('${senderId}')"] .message.unread`);

    // Mark each unread message as read
    unreadMessages.forEach(function(message) {
        const messageId = message.getAttribute('data-message-id');
        markMessageAsRead(messageId);
    });
}

function markMessageAsRead(messageId) {
    // Get the CSRF token from the cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    fetch(`/mark_as_read/${messageId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({})
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text) });
        }
        return response.json();
    })
    .then(data => {
        console.log('Message marked as read successfully:', data);
        // Update the UI to indicate the message has been read
        const messageElement = document.querySelector(`.message[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.classList.remove('unread');
        }
        updateUnreadCount();

        // Notify the server that the message has been read
        if (webSocket && webSocket.readyState === WebSocket.OPEN) {
            webSocket.send(JSON.stringify({
                'type': 'mark_as_read',
                'message_id': messageId
            }));
        }
    })
    .catch(error => {
        console.error('Error marking message as read:', error);
    });
}


// Debounce function
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// Update unread count
const updateUnreadCount = debounce(function() {
    fetch("/update_unread_count/")
        .then(response => response.json())
        .then(data => {
            updateUnreadCountBadge(data.unread_count);
        });
}, 10000);

function animateNewMessages() {
    var newMessages = document.querySelectorAll(".message.animate__animated");
    newMessages.forEach(function(message) {
        message.classList.add("animate__fadeIn");
    });
}

// Add collapsible functionality to conversation cards
window.onload = function() {
    var conversationCards = document.querySelectorAll(".conversation-card");
    conversationCards.forEach(function(card) {
        var messageList = card.querySelector(".message-list");
        if (messageList) {
            card.addEventListener("click", function() {
                messageList.classList.toggle("show");
                card.classList.toggle("expanded");
            });
        }
    });

    // Call updateUnreadCount when the page loads
    updateUnreadCount();

    // Call initWebSocketConnection when the page loads
    initWebSocketConnection();
};

// Add lazy loading of messages
window.addEventListener("scroll", function() {
  loadVisibleMessages();
});

function loadVisibleMessages() {
  var conversationCards = document.querySelectorAll(".conversation-card");
  conversationCards.forEach(function(card) {
      var messageList = card.querySelector(".message-list");
      var messages = messageList.querySelectorAll(".message:not([style*='display: none'])");
      messages.forEach(function(message) {
          if (isElementInViewport(message)) {
              message.classList.add("animate__animated", "animate__fadeIn");
          }
      });
  });
}

function isElementInViewport(element) {
  var rect = element.getBoundingClientRect();
  return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.right <= (window.innerWidth || document.documentElement.clientWidth)
  );
}
let checkForNewMessagesInterval;

function startCheckingForNewMessages() {
    checkForNewMessagesInterval = setInterval(checkForNewMessages, 2000);
}

function stopCheckingForNewMessages() {
    clearInterval(checkForNewMessagesInterval);
}

function checkForNewMessages() {
    fetch('/update_unread_count/')
        .then(response => response.json())
        .then(data => {
            updateUnreadCountBadge(data.unread_count);
        })
        .catch(error => {
            console.error('Error checking for new messages:', error);
        });
}

function updateUnreadCountBadge(count) {
    const unreadCountElement = document.getElementById('unread-count');
    if (count > 0) {
        unreadCountElement.textContent = count;
        unreadCountElement.style.display = 'inline-block';
    } else {
        unreadCountElement.style.display = 'none';
    }
}

// Add this to your window.onload event handler
window.addEventListener('load', startCheckingForNewMessages);

// Add this to your window.onunload event handler
window.addEventListener('unload', stopCheckingForNewMessages);
