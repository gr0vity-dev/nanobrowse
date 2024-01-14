
document.addEventListener("DOMContentLoaded", function() {
    handleCopyEvent('.copy_btn', 'append');
    handleCopyEvent('.copy_btn_front', 'prepend');
});

document.addEventListener('DOMContentLoaded', function() {
    let account = document.body.getAttribute('data-get-delegators-for-account');
    if (account) {
            fetchDelegatorsData(account);
    }
});
        
function __fetchDelegatorsData(account) {
    fetch(`/delegators/${account}`)
    .then(response => response.text())  // Note that we're fetching text (HTML) now
    .then(renderedTableRows => {
        let tableBody = document.querySelector("#delegatorTable tbody");
        tableBody.innerHTML = renderedTableRows;
        
    handleCopyEvent('.copy_btn', 'append');
    handleCopyEvent('.copy_btn_front', 'prepend'); 
    });
}

function fetchDelegatorsData(account) {
    fetch(`/delegators/${account}`)
    .then(response => response.text())  
    .then(renderedTableRows => {
        let tableBody = document.querySelector("#delegatorTable tbody");
        tableBody.innerHTML = renderedTableRows;
        
        document.getElementById('loadingSpinnerRow').style.display = 'none'; // hide the spinner row

        handleCopyEvent('.copy_btn', 'append');
        handleCopyEvent('.copy_btn_front', 'prepend'); 
    })
    .catch(err => {
        console.error("Error fetching delegators data:", err);
        let tableBody = document.querySelector("#delegatorTable tbody");
        tableBody.innerHTML = "<tr><td colspan='3'>Failed to load data. Please try again.</td></tr>";
    });
}


function handleCopyEvent(selector, position) {
    var copyElements = document.querySelectorAll(selector);

    copyElements.forEach(function(el) {
        // Check if the element already has the copy icon
        if (el.getAttribute('data-has-copy-icon')) {
            return;  // Skip this iteration if it already has the copy icon
        }

        var copyIcon = document.createElement('span');
        copyIcon.innerHTML = '<i class="fa-regular fa-copy"></i>';
        copyIcon.classList.add('copy_icon');

        copyIcon.addEventListener('click', function(event) {
            event.preventDefault();   // prevent the default behavior
            event.stopPropagation(); // prevent event from bubbling up

            var copyValue = el.getAttribute('data-value').trim();
            var textArea = document.createElement("textarea");
            textArea.value = copyValue;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("Copy");
            textArea.remove();

            // Change to the solid icon after copying
            copyIcon.innerHTML = '<i class="fa-solid fa-copy"> </i>';

            // Revert back to the regular icon after 2 seconds
            setTimeout(function() {
                copyIcon.innerHTML = '<i class="fa-regular fa-copy"> </i>';
            }, 1000);
        });

        if (position === 'append') {
            el.appendChild(copyIcon);
        } else if (position === 'prepend') {
            el.insertBefore(copyIcon, el.firstChild);
        }

        // Mark this element as having the copy icon
        el.setAttribute('data-has-copy-icon', 'true');
    });
}


