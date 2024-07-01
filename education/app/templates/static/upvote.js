document.addEventListener('DOMContentLoaded', function() {
    initializeVotingButtons();
});

document.addEventListener('htmx:afterSwap', function(event) {
    initializeVotingButtons();
});

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

function getCookie(name) {
    const cookieValue = document.cookie.split('; ').find(row => row.startsWith(name + '='));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}