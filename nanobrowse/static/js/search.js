const MAX_PREVIEW_COUNT = 10;
const ACCOUNT_PREFIXES = ["xrb_", "nano_"];
const HASH_LENGTH = 64;

// Utility function to set display style for a given element
function setDisplayStyle(elementId, displayStyle) {
    document.getElementById(elementId).style.display = displayStyle;
}

// Shows a specific section based on the section ID
function showSection(sectionId) {
    const sections = ['confirmationHistory', 'representatives'];
    sections.forEach(id => {
        setDisplayStyle(id, id === sectionId ? 'block' : 'none');
    });
}

// Filters and displays suggestions based on input value
function showSuggestions(value) {
    const suggestionsContainer = document.getElementById('suggestions');
    suggestionsContainer.innerHTML = '';

    if (value.length > 0) {
        const filteredAccounts = knownAccounts
            .filter(account => account.name.toLowerCase().includes(value.toLowerCase()))
            .slice(0, MAX_PREVIEW_COUNT);

        filteredAccounts.forEach(account => createSuggestionDiv(account, suggestionsContainer));
    }
}

// Creates and appends a suggestion div to the container
function createSuggestionDiv(account, container) {
    const div = document.createElement('div');
    div.innerHTML = `${account.name} (${account.account_formatted}) [${account.source}]`;
    div.onclick = () => selectAccount(account);
    container.appendChild(div);
}

// Sets the search input value and clears suggestions
function selectAccount(account) {
    const searchInput = document.querySelector('[name="blockhash"]');
    searchInput.value = account.account;
    document.getElementById('suggestions').innerHTML = '';
    handleFormSubmit();
}

// Handles the form submission logic
function handleFormSubmit(event) {
    if (event) event.preventDefault();

    const inputValue = document.querySelector('[name="blockhash"]').value.trim();

    if (ACCOUNT_PREFIXES.some(prefix => inputValue.startsWith(prefix))) {
        redirectTo(`/account/${inputValue}`);
    } else if (inputValue.length === HASH_LENGTH) {
        redirectTo(`/block/${inputValue}`);
    } else {
        alert("Invalid input. Please enter a valid account or block hash.");
    }
}

function redirectTo(url) {
    window.location.href = url;
}



// Loads known accounts from the server
async function loadKnownAccounts() {
    knownAccounts = await fetchData('/api/search/known_accounts');
}

// Initializes the application
document.addEventListener('DOMContentLoaded', () => {
    loadKnownAccounts();
});

document.addEventListener('DOMContentLoaded', function() {
    // Determine which div to display based on URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const showReps = urlParams.has('reps');  // Checks if 'reps' parameter is present in the URL
    
    // Identifiers for the div elements
    const confirmationHistoryID = 'confirmationHistory';
    const representativesID = 'representatives';
    
    // Get the div elements
    const confirmationHistoryDiv = document.getElementById(confirmationHistoryID);
    const representativesDiv = document.getElementById(representativesID);

    // Show the appropriate div based on the presence of 'reps' URL parameter
    if (showReps) {
      if (confirmationHistoryDiv) confirmationHistoryDiv.style.display = 'none'; // Hide confirmation history
      if (representativesDiv) representativesDiv.style.display = 'block'; // Show representatives
    } else {
      if (confirmationHistoryDiv) confirmationHistoryDiv.style.display = 'block'; // Show confirmation history
      if (representativesDiv) representativesDiv.style.display = 'none'; // Ensure representatives is hidden
    }
  });