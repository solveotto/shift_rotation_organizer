// Shift Colors Module
// Applies CSS classes to shift table cells based on start time

export class ShiftColors {
    constructor() {
        this.boundaries = [
            { maxMinutes: 6 * 60,    className: 'night-early' },
            { maxMinutes: 8 * 60,    className: 'morning' },
            { maxMinutes: 12 * 60,   className: 'midday' },
            { maxMinutes: 17 * 60,   className: 'afternoon' },
            { maxMinutes: Infinity,  className: 'evening' }
        ];
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.applyShiftColors();
            });
        } else {
            // DOM already loaded
            this.applyShiftColors();
        }
    }

    applyShiftColors() {
        // Skip if custom color settings are active (user has configured custom colors)
        if (localStorage.getItem('shiftColorSettings')) {
            return;
        }

        this.colorAllCells();
    }

    colorAllCells() {
        const tds = document.querySelectorAll('td[id="cell"]');

        tds.forEach(td => this.colorCell(td));
    }

    colorCell(td) {
        const timeTextElement = td.querySelector('.time-text');
        if (!timeTextElement) return;

        // Clean up the timeText by removing newline characters and extra spaces
        let timeText = timeTextElement.textContent.trim();
        timeText = timeText.replace(/\s+/g, ' '); // Replace multiple spaces with a single space

        const times = timeText.split(' - ').map(time => time.trim());
        const customTextElement = td.querySelector('.custom-text');

        // Check if custom text ends with 'H' (Holiday)
        if (customTextElement && customTextElement.textContent.trim().endsWith('H')) {
            td.classList.add('h-dag');
            return;
        }

        if (times.length > 1) {
            this.applyShiftTypeColors(td, times);
        } else {
            this.applyDayOffColors(td, times);
        }
    }

    applyShiftTypeColors(td, times) {
        const [startHours, startMinutes] = times[0].split(':').map(Number);
        const startTotal = startHours * 60 + startMinutes;

        for (const { maxMinutes, className } of this.boundaries) {
            if (startTotal < maxMinutes) {
                td.classList.add(className);
                return;
            }
        }
    }

    applyDayOffColors(td, times) {
        const listOfDaysoff = ['XX', 'OO', 'TT', ''];
        if (listOfDaysoff.includes(times[0])) {
            td.classList.add('day_off');
        }
    }

    // Method to manually trigger color application (useful for dynamic content)
    refresh() {
        this.colorAllCells();
    }

    // Method to clear all color classes
    clearColors() {
        const classes = this.boundaries.map(b => b.className).concat(['day_off', 'h-dag']);
        document.querySelectorAll('td[id="cell"]').forEach(td => {
            td.classList.remove(...classes);
        });
    }
}
