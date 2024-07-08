/**
 * Voting System for Forum Posts
 *
 * This script implements a voting system for forum posts, allowing users to upvote or downvote
 * posts. It handles the UI updates and communicates with the server to record votes.
 *
 * Features:
 * - Upvoting and downvoting functionality for posts
 * - Dynamic vote count updates
 * - Visual feedback (color) for user's current vote
 * - Integration with HTMX for dynamic content updates
 * - CSRF token handling for secure POST requests
 *
 * Main Functions:
 * - initializeVotingButtons(): Sets up event listeners for voting buttons
 * - handleVote(): Manages the voting process and updates
 * - updateVoteColors(): Updates the visual state of voting buttons
 * - getCookie(): Retrieves a cookie value by name
 *
 * Usage:
 * The script automatically initializes when the DOM content is loaded and reinitializes
 * after HTMX content swaps to ensure proper functionality with dynamically loaded content.
 */

// Initialize voting buttons when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeVotingButtons();
});

// Reinitialize voting buttons after HTMX content swaps
document.addEventListener('htmx:afterSwap', function(event) {
    initializeVotingButtons();
});

/**
 * Initializes voting buttons for all voting containers on the page.
 * Sets up event listeners for upvote and downvote buttons and updates their initial colors.
 */
function initializeVotingButtons() {
    const votingContainers = document.querySelectorAll('.voting');
    votingContainers.forEach(container => {
        const postId = container.dataset.postId;
        if (postId) {
            const upvoteButton = container.querySelector('.upvote');
            const downvoteButton = container.querySelector('.downvote');
            const upvoteCount = container.querySelector('.upvote-count');

            upvoteButton.addEventListener('click', () => handleVote(postId, 'upvote', upvoteCount, upvoteButton, downvoteButton));
            downvoteButton.addEventListener('click', () => handleVote(postId, 'downvote', upvoteCount, upvoteButton, downvoteButton));

            updateVoteColors(upvoteButton, downvoteButton, postId);
        }
    });
}

/**
 * Handles the voting process when a user clicks an upvote or downvote button.
 * Sends a POST request to the server and updates the UI accordingly.
 *
 * @param {string} postId - The ID of the post being voted on
 * @param {string} voteType - The type of vote ('upvote' or 'downvote')
 * @param {HTMLElement} upvoteCountElement - The element displaying the vote count
 * @param {HTMLElement} upvoteButton - The upvote button element
 * @param {HTMLElement} downvoteButton - The downvote button element
 */
function handleVote(postId, voteType, upvoteCountElement, upvoteButton, downvoteButton) {
    const url = `/${voteType}/${postId}/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        upvoteCountElement.textContent = data.upvote_count;
        updateVoteColors(upvoteButton, downvoteButton, postId);
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally, show an error message to the user
    });
}

/**
 * Updates the colors of the voting buttons based on the user's current vote.
 * Sends a POST request to get the current vote status and updates button colors.
 *
 * @param {HTMLElement} upvoteButton - The upvote button element
 * @param {HTMLElement} downvoteButton - The downvote button element
 * @param {string} postId - The ID of the post
 */
function updateVoteColors(upvoteButton, downvoteButton, postId) {
    const url = `/vote_color/${postId}/`;
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        let colorvote = data.vote;
        if (colorvote === 0) {
            upvoteButton.style.color = '';
            downvoteButton.style.color = '';
        } else if (colorvote === 1) {
            upvoteButton.style.color = 'green';
            downvoteButton.style.color = '';
        } else if (colorvote === -1) {
            upvoteButton.style.color = '';
            downvoteButton.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // Optionally, show an error message to the user
    });
}

/**
 * Retrieves the value of a cookie by its name.
 *
 * @param {string} name - The name of the cookie to retrieve (CSRF token in this case)
 * @returns {string|null} The value of the cookie if found, null otherwise
 */
function getCookie(name) {
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}
