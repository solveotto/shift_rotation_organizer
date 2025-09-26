// Shift Colors Module
// Applies CSS classes to shift table cells based on time and shift type

export class ShiftColors {
    constructor() {
        this.defaultTimeThresholds = {
            lateShift: 16 * 60,  // 16:00 in minutes
            nightShift: 19 * 60  // 19:00 in minutes
        };
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
        if (!timeTextElement) {
            console.log('No .time-text element found in td:', td);
            return;
        }

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
        const startTime = times[0];
        const [start_hours, start_minutes] = startTime.split(':').map(Number);
        const startTotalMinutes = start_hours * 60 + start_minutes;

        const endTime = times[1];
        const [end_hours, end_minutes] = endTime.split(':').map(Number);
        const endTotalMinutes = end_hours * 60 + end_minutes;

        // Apply color classes based on shift timing
        if (endTotalMinutes <= this.defaultTimeThresholds.lateShift) {
            td.classList.add('early');
        }
        if (endTotalMinutes > this.defaultTimeThresholds.lateShift) {
            td.classList.add('late');
        }
        if (startTotalMinutes >= this.defaultTimeThresholds.nightShift) {
            td.classList.add('night');
        }
        if (startTotalMinutes > endTotalMinutes) {
            td.classList.add('late');
        }

        // Check for early-and-late shift combination
        if (start_hours > 5 && start_hours < 9 && end_hours >= 16 && end_hours < 18) {
            td.classList.add('early-and-late');
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
        const tds = document.querySelectorAll('td[id="cell"]');
        tds.forEach(td => {
            td.classList.remove('early', 'late', 'night', 'day_off', 'h-dag', 'early-and-late');
        });
    }
}