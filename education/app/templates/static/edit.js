document.addEventListener("DOMContentLoaded", function () {
    attachEditAndSaveEventListeners();

    // Listen for the htmx:afterRequest event to reattach event listeners if needed
    document.addEventListener("htmx:afterRequest", function (event) {
        attachEditAndSaveEventListeners();
    });
});

function attachEditAndSaveEventListeners() {
    const commonAncestor = document.querySelector("body");

    const handleButtonClick = function (event) {
        const target = event.target;
        let button;

        // Check if the target is the button itself or a child element (e.g., the SVG icon)
        if (target.classList.contains("edit-button")) {
            button = target;
        } else {
            button = target.closest(".edit-button");
        }

        if (button) {
            handleEditButtonClick(event, button);
        } else if (target.classList.contains("save-button")) {
            handleSaveButtonClick(event);
        }
    };

    if (commonAncestor) {
        commonAncestor.addEventListener("click", handleButtonClick);
        console.log("Event listeners attached using event delegation to common ancestor");
    } else {
        console.error("Common ancestor element not found for event delegation.");
    }
}

function handleEditButtonClick(event, button) {
    console.log("Edit button clicked");
    const threadId = button.getAttribute("data-thread-id");
    const postId = button.getAttribute("data-post-id");
    const isThreadPost = threadId !== null;

    // Determine the appropriate IDs based on whether it's a thread post or a regular post
    const postTextId = isThreadPost ? `post-text-thread-${threadId}` : `post-text-${postId}`;
    const editInputId = isThreadPost ? `edit-input-thread-${threadId}` : `edit-input-${postId}`;
    const saveButtonId = isThreadPost ? `save-button-thread-${threadId}` : `save-button-${postId}`;

    // Get the DOM elements
    const postText = document.getElementById(postTextId);
    const editInput = document.getElementById(editInputId);
    const saveButton = document.getElementById(saveButtonId);

    if (!postText || !editInput || !saveButton) {
        console.error("Failed to find elements for editing.");
        return;
    }

    // Toggle visibility
    const isEditVisible = editInput.style.display === "block";
    if (isEditVisible) {
        editInput.style.display = "none";
        saveButton.style.display = "none";
        postText.style.display = "block";
    } else {
        postText.style.display = "none";
        editInput.style.display = "block";
        saveButton.style.display = "block";
        editInput.value = postText.textContent;
        editInput.focus();
    }
}

function handleSaveButtonClick(event) {
    console.log("Save button clicked");
    const button = event.target;
    const threadId = button.getAttribute("data-thread-id");
    const postId = button.getAttribute("data-post-id");
    const isThreadPost = threadId !== null;

    // Determine the appropriate IDs based on whether it's a thread post or a regular post
    const editInputId = isThreadPost ? `edit-input-thread-${threadId}` : `edit-input-${postId}`;
    const postTextId = isThreadPost ? `post-text-thread-${threadId}` : `post-text-${postId}`;

    // Get the DOM elements
    const editInput = document.getElementById(editInputId);
    const postText = document.getElementById(postTextId);
    const newText = editInput.value;

    if (newText.trim() === '') {
        console.error("New text is empty");
        button.classList.remove("saving");
        button.disabled = false;
        return;
    }
    
    // Add 'saving' state class and disable the button to prevent multiple clicks
    button.classList.add("saving");
    button.disabled = true;

    // Determine the appropriate URL based on whether it's a thread post or a regular post
    const url = isThreadPost ? `/save_thread/${threadId}/` : `/save_post/${postId}/`;
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    // Make a fetch request to save the updated post
    fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({ text: newText })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the post text with the new text
            postText.textContent = newText;

            // Hide the edit input and save button, and show the updated post text
            editInput.style.display = "none";
            button.style.display = "none";
            postText.style.display = "block";

            // Remove the 'saving' class and add the 'success' class to the button
            button.classList.remove("saving");
            button.classList.add("success");

            // Use a timeout to remove the 'success' class after a certain period
            setTimeout(() => {
                button.classList.remove("success");
                button.disabled = false;
            }, 2000);
        } else {
            console.error("Error updating post:", data.error);
            button.classList.remove("saving");
            button.disabled = false;
        }
    })
    .catch(error => {
        console.error("Error updating post:", error);
        button.classList.remove("saving");
        button.disabled = false;
    });
}