document.addEventListener('DOMContentLoaded', function() {
  console.log('DOMContentLoaded event fired');

  const inboxContainer = document.querySelector('.inbox-container');
  const conversationList = document.querySelector('.conversation-list');
  const conversationCard = conversationList.firstElementChild;
  const conversationCards = conversationList.querySelectorAll('.conversation-card');

  if (!inboxContainer || !conversationList || !conversationCards.length) {
    console.error('One or more elements are missing!');
    return; // Check if the elements exist
  }

  conversationCards.forEach(card => {
    const messageList = card.querySelector('.message-list');
    if (!messageList) {
      console.error('messageList not found inside conversation card');
      return; // Check if messageList exists within the card
    }

    messageList.addEventListener('click', function() {
      console.log('messageList clicked:', messageList); // Debug: log clicked messageList
      this.classList.toggle('show'); // Toggle visibility
      console.log('Current classes on messageList:', this.classList); // Debug: log classList
    });
  });

  console.log('Event listeners added to all cards');

  
  if (!inboxContainer || !conversationList || !conversationCard) {
    console.error('Failed to select inboxContainer, conversationList, or conversationCard elements');
    return;
  }

  console.log('inboxContainer, conversationList, and conversationCard elements found');

  let currentPage = 1;
  let isLoading = false;
  let nextPageUrl;

  window.loadMoreMessages = async function() { // Expose for global access, debug only
    if (isLoading) {
      console.log('loadMoreMessages function already running, returning');
      return;
    }

    console.log('loadMoreMessages function called');
    isLoading = true;

    try {
      const response = await fetch(nextPageUrl || '/inbox/messages/?page=1');

      if (!response.ok) {
        console.error('Error fetching messages:', response.status, response.statusText);
        isLoading = false;
        return;
      }

      console.log('Fetch request successful');

      const data = await response.json();
      nextPageUrl = data.next_page_url;

      if (data.messages.length > 0) {
        console.log(`${data.messages.length} new messages fetched`);

        const messageList = conversationCard.querySelector('.message-list');

        if (messageList) {
          console.log('messageList element found:', messageList);
          data.messages.forEach(message => {
            console.log('Message content:', message.content);
            console.log('Message sender:', message.sender);

            const messageElement = document.createElement('div');
            messageElement.classList.add('message', message.sender === '{{ request.user.id }}' ? 'sender' : 'receiver');
            if (!message.is_read) {
              messageElement.classList.add('unread');
            }
            messageElement.dataset.messageId = message.id;
            messageElement.innerHTML = `<div class="message-content"><p>${message.content}</p></div>`;
          });
        } else {
          console.error('Failed to find messageList element');
        }
      } else {
        console.log('No more messages to load');
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      isLoading = false;
      console.log('loadMoreMessages function completed');
    }
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting && !isLoading) {
        console.log('Reached bottom of message list, loading more messages');
        loadMoreMessages();
      }
    });
  }, { root: conversationCard, rootMargin: '0px 0px 100px 0px' });

  const sentinel = document.createElement('div');
  sentinel.classList.add('sentinel');
  conversationCard.appendChild(sentinel);
  observer.observe(sentinel);
});