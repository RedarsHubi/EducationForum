document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('#search-input');
  const searchButton = document.querySelector('#search-button');
  const suggestionsContainer = document.querySelector('#suggestions-container');
  const sectionDropdown = document.querySelector('#filter-section');
  const categoryDropdown = document.querySelector('#filter-category');
  const filterOptions = document.querySelector('#filter-options');
  const filterButton = document.querySelector('#filter-button');

  // Function to fetch search suggestions from the server
  async function fetchSuggestions(query) {
      try {
          const response = await fetch(`/search/suggestions/?q=${encodeURIComponent(query)}`);
          const suggestions = await response.json();
          return suggestions;
      } catch (error) {
          console.error('Error fetching suggestions:', error);
          return [];
      }
  }

  // Function to display search suggestions
  async function showSuggestions(query) {
      const suggestions = await fetchSuggestions(query);
      suggestionsContainer.innerHTML = ''; // Clear previous suggestions
      if (suggestions.length > 0) {
          suggestions.forEach(suggestion => {
              // Truncate suggestion text to display only a few words
              const truncatedSuggestion = truncateText(suggestion, 10); // Adjust the number of words as needed
              const suggestionElement = document.createElement('div');
              suggestionElement.classList.add('suggestion');
              suggestionElement.textContent = truncatedSuggestion;
              suggestionsContainer.appendChild(suggestionElement);

              // Add click event listener to hide suggestions when clicked
              suggestionElement.addEventListener('click', function() {
                  searchInput.value = suggestion; // Set the full suggestion text to the input
                  hideSuggestions();
                  handleSearch(); // Perform search when suggestion is clicked
              });
          });
          suggestionsContainer.style.display = 'block'; // Show suggestions
      } else {
          suggestionsContainer.style.display = 'none'; // Hide suggestions if there are none
      }
  }

  // Function to truncate text
  function truncateText(text, maxLength) {
      const words = text.split(' ');
      if (words.length > maxLength) {
          return words.slice(0, maxLength).join(' ') + '...'; // Truncate and add ellipsis
      } else {
          return text;
      }
  }

  // Function to hide suggestions
  function hideSuggestions() {
      suggestionsContainer.style.display = 'none';
  }

  // Function to update categories based on selected section
  async function updateCategories() {
      const section = sectionDropdown.value;
      try {
          const response = await fetch(`/get_categories/?section=${encodeURIComponent(section)}`);
          const categories = await response.json();
          categoryDropdown.innerHTML = ''; // Clear existing categories
          categories.forEach(category => {
              const option = document.createElement('option');
              option.value = category.name;
              option.textContent = category.name;
              categoryDropdown.appendChild(option);
          });
      } catch (error) {
          console.error('Error fetching categories:', error);
      }
  }

  // Function to handle search
  function handleSearch() {
      const query = searchInput.value.trim();
      const category = categoryDropdown.value; // Get the selected category value
      const dateFilter = document.querySelector('#filter-date').value || 'any';
      const authorFilter = document.querySelector('#filter-author').value.trim();
      
      if (query || category || dateFilter || authorFilter)  {
          // Redirect to the search results page with query, category, and other filters
          window.location.href = `/search/results/?q=${encodeURIComponent(query)}&category=${encodeURIComponent(category)}&date=${dateFilter}&author=${encodeURIComponent(authorFilter)}`;
      }
  }

  // Attach event listener for input change
  searchInput.addEventListener('input', function(event) {
      const query = searchInput.value.trim();
      if (query) {
          showSuggestions(query);
      } else {
          hideSuggestions();
      }
  });

  // Handle search button click
  searchButton.addEventListener('click', handleSearch);

  // Handle "Enter" key press in the search input field
  searchInput.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
          event.preventDefault(); // Prevent default form submission behavior
          handleSearch();
      }
  });

  // Hide suggestions when clicking outside the search input
  document.addEventListener('click', function(event) {
      if (!searchInput.contains(event.target)) {
          hideSuggestions();
      }
  });

  // Attach event listener for section dropdown change
  sectionDropdown.addEventListener('change', updateCategories);

  // Function to toggle filter options visibility
  function toggleFilterOptions() {
      filterOptions.classList.toggle('hidden');
  }

  // Attach event listener for filter button click
  filterButton.addEventListener('click', toggleFilterOptions);
  document.addEventListener('click', function(event) {
      if (!filterButton.contains(event.target) && !filterOptions.contains(event.target)) {
          filterOptions.classList.add('hidden');
      }
  });
});