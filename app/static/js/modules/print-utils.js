// Print Utilities Module

export class PrintUtils {
    static printTables() {
        var printContents = '';
        var tables = document.querySelectorAll('table');
        
        tables.forEach(function(table) {
            var container = table.closest('li') || table.closest('div.list-group-item');
            var name = container.querySelector('.t-name').innerText;
            
            // Try to get the number, but don't fail if it doesn't exist
            var numberElement = container.querySelector('.t-num');
            var number = numberElement ? numberElement.innerText + ' - ' : '';
            
            // Try to get the data stats, but don't fail if it doesn't exist
            var dataFeltElement = container.querySelector('.data-felt');
            var dataFelt = dataFeltElement ? dataFeltElement.outerHTML : '';
            
            printContents += '<div class="print-frame"><h4>' + number + name + '</h4>' + table.outerHTML + dataFelt + '</div><br>';
        });

        var originalContents = document.body.innerHTML;
        document.body.innerHTML = printContents;
        window.print();
        document.body.innerHTML = originalContents;
    }

    static disableSubmitButton(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerText = 'Submitting...';
        }
        return true;  // Ensure the form is submitted
    }
}

// Make functions available globally for backward compatibility
window.printTables = PrintUtils.printTables;
window.disableSubmitButton = PrintUtils.disableSubmitButton;
