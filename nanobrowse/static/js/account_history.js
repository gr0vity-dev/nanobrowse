manuallyToggled = null;

document.addEventListener('DOMContentLoaded', () => {    
    const account = document.body.getAttribute('data-get-delegators-for-account');
    if (account) {
      const url = `/account_history/${account}`;
      fetchRenderedData(url, '#account_history_table').then(() => {        
        hideElement('accountHistorySpinner');
        handleCopyEvent(".copy_btn", "append");
        handleCopyEvent(".copy_btn_front", "prepend");
        loadInitialTable();
      });
    } 
  });
  
  function loadInitialTable() {
    document.querySelectorAll('.table').forEach(table => {
        if (table.id !== manuallyToggled) {
            table.style.display = 'none';
        }
    });
    if (manuallyToggled) {
        console.log("return");
         return;
    }

    // Determine which table to display based on URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const showGrouped = urlParams.has('grouped');
    const defaultTableID = showGrouped ? 'groupedTransactionTable' : 'transactionTable';  
    
    // Show the appropriate one
    const defaultTable = document.getElementById(defaultTableID);
    if (defaultTable) {
      defaultTable.style.display = 'table';
    } else {
      console.error(`Table with ID ${defaultTableID} not found.`);
    }
  }
  
// Event listener for toggling tables
document.addEventListener('click', function(event) {
    let targetElement = event.target;   
    console.log(manuallyToggled)
  
    // Traverse up the DOM to find an element with 'data-show-table' attribute
    while (targetElement && targetElement !== document.body && !targetElement.getAttribute('data-show-table')) {
      targetElement = targetElement.parentElement;
    }
  
    // Toggle table display if a valid target is found
    if (targetElement && targetElement.getAttribute('data-show-table')) {
      manuallyToggled = targetElement.getAttribute('data-show-table');

      switch (targetElement.getAttribute('data-show-table')) {
        case 'transactionTable':
          document.getElementById('tableSubBtns').classList.remove('hidden');
          document.getElementById('tableSubBtns').classList.add('flex');
          highlight(['transactionTableBtn', 'transactionTableSubBtn']);
          break;
        case 'groupedTransactionTable':
          document.getElementById('tableSubBtns').classList.remove('hidden');
          document.getElementById('tableSubBtns').classList.add('flex');
          highlight(['transactionTableBtn', 'groupedTransactionTableSubBtn']);
          break;
        case 'receivableTable':
          document.getElementById('tableSubBtns').classList.add('hidden');
          document.getElementById('tableSubBtns').classList.remove('flex');
          highlight(['receivableTableBtn']);
          break;
        case 'delegatorTable':
          document.getElementById('tableSubBtns').classList.add('hidden');
          document.getElementById('tableSubBtns').classList.remove('flex');
          highlight(['delegatorTableBtn']);
          break;
      }

      const targetTableID = targetElement.getAttribute('data-show-table');
      document.querySelectorAll('.table').forEach(table => table.style.display = 'none');
      const targetTable = document.getElementById(targetTableID);
      if (targetTable) {
        targetTable.style.display = 'table';
      } else {
        console.error(`Table with ID ${targetTableID} not found.`);
      }
    }
  });

function highlight(ids) {
  // Reset color of all table-selection buttons:
  document.querySelectorAll(`[data-show-table]`).forEach(element => {
    element.classList.add(element.getAttribute('data-default-color'));
    element.classList.remove(element.getAttribute('data-active-color'));
  });

  // Highlight given elements:
  ids.forEach(id => {
    let element = document.getElementById(id);
    if (element) {
      element.classList.remove(element.getAttribute('data-default-color'));
      element.classList.add(element.getAttribute('data-active-color'));
    }
  });
}
