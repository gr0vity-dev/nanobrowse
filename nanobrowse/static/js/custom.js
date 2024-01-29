document.addEventListener("DOMContentLoaded", () => {
    const account = document.body.getAttribute("data-get-delegators-for-account");
    if (account) {
      fetchDelegatorsData(account);
    }
  
    handleCopyEvent(".copy_btn", "append");
    handleCopyEvent(".copy_btn_front", "prepend");
  });
  
  function fetchDelegatorsData(account) {
    fetch(`/delegators/${account}`)
      .then(response => response.text())
      .then(renderedTableRows => updateTableWithDelegators(renderedTableRows))
      .catch(error => handleFetchError(error));
  }
  
  function updateTableWithDelegators(renderedTableRows) {
    const tableBody = document.querySelector("#delegatorTable tbody");
    tableBody.innerHTML = renderedTableRows;
  
    hideElement("loadingSpinnerRow");
  
    handleCopyEvent(".copy_btn", "append");
    handleCopyEvent(".copy_btn_front", "prepend");
  }
  
  function hideElement(elementId) {
    document.getElementById(elementId).style.display = "none";
  }
  
  function handleFetchError(error) {
    console.error("Error fetching delegators data:", error);
    const tableBody = document.querySelector("#delegatorTable tbody");
    tableBody.innerHTML = "<tr><td colspan='3'>Failed to load data. Please try again.</td></tr>";
  }
  
  function handleCopyEvent(selector, position) {
    const copyElements = document.querySelectorAll(selector);
  
    copyElements.forEach(el => {
      if (!el.getAttribute("data-has-copy-icon")) {
        addCopyIcon(el, position);
      }
    });
  }
  
  function addCopyIcon(element, position) {
    const copyIcon = createCopyIcon();
  
    copyIcon.addEventListener("click", event => copyToClipboard(event, element));
  
    if (position === "append") {
      element.appendChild(copyIcon);
    } else if (position === "prepend") {
      element.insertBefore(copyIcon, element.firstChild);
    }
  
    element.setAttribute("data-has-copy-icon", "true");
  }
  
  function createCopyIcon() {
    const copyIcon = document.createElement("span");
    copyIcon.innerHTML = '<i class="fa-regular fa-copy"></i>';
    copyIcon.classList.add("copy_icon");
    return copyIcon;
  }
  
  function copyToClipboard(event, element) {
    event.preventDefault();
    event.stopPropagation();
  
    const copyValue = element.getAttribute("data-value").trim();
    const textArea = document.createElement("textarea");
    textArea.value = copyValue;
  
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("Copy");
    textArea.remove();
  
    updateCopyIcon(element.querySelector(".copy_icon"));
  }
  
  function updateCopyIcon(copyIcon) {
    copyIcon.innerHTML = '<i class="fa-solid fa-copy"> </i>';
  
    setTimeout(() => {
      copyIcon.innerHTML = '<i class="fa-regular fa-copy"> </i>';
    }, 1000);
  }
  