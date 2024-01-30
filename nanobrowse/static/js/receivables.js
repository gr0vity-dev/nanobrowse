document.addEventListener("DOMContentLoaded", () => {
    const account = document.body.getAttribute("data-get-delegators-for-account");
    if (account) {
        fetchRenderedData(`/receivables/${account}`, `#pendingTable tbody`).then(() => {            
            hideElement("pendingSpinner"); 
            handleCopyEvent(".copy_btn", "append");
            handleCopyEvent(".copy_btn_front", "prepend");
        });    
    }  
});