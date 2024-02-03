document.addEventListener("DOMContentLoaded", () => {
  handleCopyEvent(".copy_btn", "append");
  handleCopyEvent(".copy_btn_front", "prepend");
});

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

function fetchRenderedData(url, updateElementId) {
  return fetch(url)
    .then((response) => response.text())
    .then((renderedTableRows) => updateElement(renderedTableRows, updateElementId))
    .catch((error) => handleFetchError(error, updateElementId));
}

function updateElement(renderedTableRows, updateElementId) {
  // Create a temporary container for the new content
  const tempContainer = document.createElement('div');
  tempContainer.innerHTML = renderedTableRows;  
  const newElement = tempContainer.querySelector(updateElementId);
  const oldElement = document.querySelector(updateElementId);
  oldElement.parentNode.replaceChild(newElement, oldElement);
}


function handleFetchError(error, updateElementId) {
  console.error("Error fetching Data:", error);
  const tableBody = document.querySelector(updateElementId);
  tableBody.innerHTML =
    "<tr><td colspan='3'>Failed to load data. Please try again.</td></tr>";
}

function hideElement(elementId) {
  document.getElementById(elementId).style.display = "none";
}

function handleCopyEvent(selector, position) {
  const copyElements = document.querySelectorAll(selector);

  copyElements.forEach((el) => {
    if (!el.getAttribute("data-has-copy-icon")) {
      addCopyIcon(el, position);
    }
  });
}

function addCopyIcon(element, position) {
  const copyIcon = createCopyIcon();

  copyIcon.addEventListener("click", (event) =>
    copyToClipboard(event, element)
  );

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
