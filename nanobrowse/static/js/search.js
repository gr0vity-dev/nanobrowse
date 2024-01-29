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

async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Loads known accounts from the server
async function loadKnownAccounts() {
    knownAccounts = await fetchData('/api/search/known_accounts');
}

// Initializes the application
document.addEventListener('DOMContentLoaded', () => {
    loadKnownAccounts();
});
