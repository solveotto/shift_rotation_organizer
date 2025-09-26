// Shift Selection Module
// Handles clickable rows and shift selection functionality

export class ShiftSelection {
    constructor() {
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupClickableRows();
            this.setupCheckboxes();
        });
    }

    setupClickableRows() {
        document.querySelectorAll('.clickable-row').forEach(row => {
            row.addEventListener('click', () => {
                const turnus = row.getAttribute('data-turnus');
                this.selectShift(turnus);
            });
        });
    }

    setupCheckboxes() {
        // Add click event listener to checkboxes to stop propagation
        document.querySelectorAll('.prevent-click').forEach(checkbox => {
            checkbox.addEventListener('click', function(event) {
                event.stopPropagation();
            });
        });
    }

    async selectShift(turnus) {
        try {
            const response = await fetch('/api/js_select_shift', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ shift_title: turnus })
            });

            if (response.redirected) {
                window.location.href = response.url;
            } else {
                const data = await response.json();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
}
