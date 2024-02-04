document.addEventListener("DOMContentLoaded", () => {
    const account = document.body.getAttribute("data-get-delegators-for-account");
    if (account) {
        fetchRenderedData(`/receivables/${account}`, `#receivableTable tbody`).then(() => {            
            hideElement("receivableSpinner"); 
            handleCopyEvent(".copy_btn", "append");
            handleCopyEvent(".copy_btn_front", "prepend");
        });    
    }  
});