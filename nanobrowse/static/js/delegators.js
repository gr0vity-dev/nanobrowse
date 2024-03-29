document.addEventListener("DOMContentLoaded", () => {
    const account = document.body.getAttribute("data-get-delegators-for-account");
    if (account) {
        fetchRenderedData(`/delegators/${account}`, `#delegatorTable tbody`).then(() => {            
            hideElement("delegatorSpinner"); 
            handleCopyEvent(".copy_btn", "append");
            handleCopyEvent(".copy_btn_front", "prepend");
        });    
    }  
});