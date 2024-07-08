# `inbox.js` - Real-time Inbox Management System

This module manages real-time updates, message reading status, and UI interactions for an inbox system.

## WebSocket Connection

### `initWebSocketConnection()`

Establishes and manages a WebSocket connection for real-time updates.

- Handles connection opening, message reception, closing, and errors.
- Processes 'unread_count_update' and 'new_message' event types.

## Message Management

### `markConversationAsRead(senderId)`

Marks all unread messages in a conversation as read.

### `markMessageAsRead(messageId)`

Marks a single message as read:
- Sends a POST request to the server.
- Updates the UI to reflect the read status.
- Notifies the WebSocket server of the status change.

## UI Updates

### `updateUnreadCount()`

Fetches and updates the unread message count (debounced).

### `animateNewMessages()`

Applies a fade-in animation to new messages.

### `updateUnreadCountBadge(count)`

Updates the unread message count badge in the UI.

## Lazy Loading

### `loadVisibleMessages()`

Loads and animates messages as they become visible in the viewport.

### `isElementInViewport(element)`

Checks if an element is currently visible in the viewport.

## Periodic Checks

### `startCheckingForNewMessages()`

Initiates periodic checks for new messages.

### `stopCheckingForNewMessages()`

Stops periodic checks for new messages.

### `checkForNewMessages()`

Fetches the latest unread count from the server.

## Event Listeners

- Adds collapsible functionality to conversation cards on page load.
- Sets up scroll event listener for lazy loading messages.
- Initializes WebSocket connection and periodic checks on page load.
- Stops periodic checks on page unload.

## Utility Functions

### `debounce(func, delay)`

Implements debouncing to limit the frequency of function calls.

## Note on Security

The code includes a CSRF token in POST requests, enhancing security for server communications.

# `fix.js` - Inbox Message Loading System

This JavaScript module manages the loading and display of messages in an inbox-style interface.

## Event Listeners

The script sets up event listeners when the DOM content is loaded:

- It adds click listeners to each `messageList` within `conversationCards` to toggle their visibility.
- It sets up an Intersection Observer to detect when the user has scrolled to the bottom of the message list.

## Main Functions

### `loadMoreMessages()`

Asynchronously fetches and displays additional messages.

Parameters: None

Behavior:
1. Checks if already loading to prevent duplicate requests.
2. Fetches the next page of messages from the server.
3. Appends new messages to the existing message list.
4. Updates the `nextPageUrl` for subsequent loads.

Note: This function is exposed globally for debugging purposes.

## Key Elements

- `.inbox-container`: The main container for the inbox interface.
- `.conversation-list`: Contains all conversation cards.
- `.conversation-card`: Represents an individual conversation.
- `.message-list`: Contains messages within a conversation card.

## Pagination

- Uses a `currentPage` variable to keep track of the loaded pages.
- `nextPageUrl` stores the URL for the next page of messages.

## Infinite Scrolling

Implemented using an Intersection Observer:
- Observes a sentinel element at the bottom of the message list.
- Triggers `loadMoreMessages()` when the sentinel becomes visible.

## Message Rendering

New messages are dynamically created and added to the DOM with the following structure:

```html
<div class="message [sender|receiver] [unread]" data-message-id="[id]">
  <div class="message-content">
    <p>[message content]</p>
  </div>
</div>
