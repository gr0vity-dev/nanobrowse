
document.addEventListener("DOMContentLoaded", function() {
    handleCopyEvent('.copy_btn', 'append');
    handleCopyEvent('.copy_btn_front', 'prepend');
});

function handleCopyEvent(selector, position) {
    var copyElements = document.querySelectorAll(selector);

    copyElements.forEach(function(el) {
        var copyIcon = document.createElement('span');
        copyIcon.innerHTML = '<i class="fa-regular fa-copy"></i>'; 
        copyIcon.classList.add('copy_icon');
        
        copyIcon.addEventListener('click', function(event) {
            event.preventDefault();   // prevent the default behavior
            event.stopPropagation(); // prevent event from bubbling up

            var textArea = document.createElement("textarea");
            textArea.value = el.innerText; // only copy the innerText, not the copy icon itself
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand("Copy");
            textArea.remove();

            // Change to the solid icon after copying
            copyIcon.innerHTML = '<i class="fa-solid fa-copy"></i>';

            // Revert back to the regular icon after 2 seconds
            setTimeout(function() {
                copyIcon.innerHTML = '<i class="fa-regular fa-copy"></i>';
            }, 1000);
        });

        if (position === 'append') {
            el.appendChild(copyIcon);
        } else if (position === 'prepend') {
            el.insertBefore(copyIcon, el.firstChild);
        }
    });
}
