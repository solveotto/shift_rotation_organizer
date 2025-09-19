// Utilities Module
// Shared utility functions

export class Utils {
    static disableSubmitButton(form) {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerText = 'Submitting...';
        }
        return true;  // Ensure the form is submitted
    }

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
}

export class ScrollPosition {
    constructor() {
        this.indexRoute = '/';
        this.specificRoute = window.location.pathname;
        this.init();
    }

    init() {
        if (window.location.pathname === this.indexRoute) {
            this.setupScrollSaving();
            this.restoreScrollPosition();
        }
    }

    setupScrollSaving() {
        // Save the scroll position before the user navigates away
        window.addEventListener('beforeunload', () => {
            localStorage.setItem('scrollPosition', window.scrollY);
        });
    }

    restoreScrollPosition() {
        // Restore the scroll position after the page has fully loaded
        window.onload = () => {
            setTimeout(() => {
                const savedPosition = localStorage.getItem('scrollPosition-' + this.specificRoute);
                if (savedPosition) {
                    window.scrollTo(0, parseInt(savedPosition));
                }
            }, 100);  // Delay restoration slightly to ensure content has loaded
        };
    }
}

// Make printTables available globally for backward compatibility
window.printTables = Utils.printTables;
window.disableSubmitButton = Utils.disableSubmitButton;
