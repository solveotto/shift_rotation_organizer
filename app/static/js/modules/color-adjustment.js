// Color Adjustment Module
// Handles the color system for shift tables

export class ColorAdjustment {
    constructor() {
        this.defaultSettings = {
            early: {
                color: '#00ffff',
                time: '16:00'
            },
            late: {
                color: '#ff9696',
                time: '16:00'
            },
            night: {
                color: '#eb41eb',
                time: '19:00'
            },
            dayoff: {
                color: '#42bb42'
            },
            hdag: {
                color: '#ffd700'
            },
            earlylate: {
                color: '#268eb8'
            }
        };
        
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            // Check if we're on the turnusliste page
            const colorPanel = document.querySelector('#apply-colors');
            if (!colorPanel) return;

            this.setupEventListeners();
            this.initializeColorInputs();
            this.applyColorsToTable();
            console.log('Color adjustment system initialized');
        });
    }

    setupEventListeners() {
        // Apply button
        const applyButton = document.getElementById('apply-colors');
        if (applyButton) {
            applyButton.addEventListener('click', () => this.handleApplyColors());
        }

        // Reset button
        const resetButton = document.getElementById('reset-colors');
        if (resetButton) {
            resetButton.addEventListener('click', () => this.handleResetColors());
        }
    }

    loadColorSettings() {
        try {
            const saved = localStorage.getItem('shiftColorSettings');
            if (saved) {
                return { ...this.defaultSettings, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.warn('Error loading color settings:', error);
        }
        return this.defaultSettings;
    }

    saveColorSettings(settings) {
        try {
            localStorage.setItem('shiftColorSettings', JSON.stringify(settings));
            console.log('Color settings saved:', settings);
        } catch (error) {
            console.error('Error saving color settings:', error);
        }
    }

    applyColorsToTable() {
        const settings = this.loadColorSettings();
        
        // Remove existing color classes
        const tds = document.querySelectorAll('td[id="cell"]');
        
        tds.forEach(td => {
            td.classList.remove('early', 'late', 'night', 'day_off', 'h-dag', 'early-and-late');
            td.style.backgroundColor = '';
            td.style.color = '';
        });

        // Apply new colors based on settings
        tds.forEach(td => this.colorCell(td, settings));
    }

    colorCell(td, settings) {
        const timeTextElement = td.querySelector('.time-text');
        if (!timeTextElement) return;

        let timeText = timeTextElement.textContent.trim();
        timeText = timeText.replace(/\s+/g, ' ');
        const times = timeText.split(' - ').map(time => time.trim());
        const customTextElement = td.querySelector('.custom-text');

        // Check for H-dag
        if (customTextElement && customTextElement.textContent.trim().endsWith('H')) {
            td.style.backgroundColor = settings.hdag.color;
            console.log('Applied H-dag color:', settings.hdag.color);
            return;
        }

        if (times.length > 1) {
            this.applyShiftColors(td, times, settings, timeText);
        } else {
            this.applyDayOffColors(td, times, settings);
        }
    }

    applyShiftColors(td, times, settings, timeText) {
        const startTime = times[0];
        const [start_hours, start_minutes] = startTime.split(':').map(Number);
        const startTotalMinutes = start_hours * 60 + start_minutes;

        const endTime = times[1];
        const [end_hours, end_minutes] = endTime.split(':').map(Number);
        const endTotalMinutes = end_hours * 60 + end_minutes;

        // Parse threshold times
        const [late_hours, late_minutes] = settings.late.time.split(':').map(Number);
        const late_shift = late_hours * 60 + late_minutes;
        
        const [night_hours, night_minutes] = settings.night.time.split(':').map(Number);
        const night_shift = night_hours * 60 + night_minutes;

        // Apply colors based on thresholds
        if (startTotalMinutes >= night_shift) {
            td.style.backgroundColor = settings.night.color;
            console.log('Applied night color:', settings.night.color);
        } else if (start_hours > 5 && start_hours < 9 && end_hours >= 16 && end_hours < 18) {
            td.style.backgroundColor = settings.earlylate.color;
            td.style.color = 'white';
            console.log('Applied early+late color:', settings.earlylate.color);
        } else if (endTotalMinutes <= late_shift) {
            td.style.backgroundColor = settings.early.color;
            console.log('Applied early color:', settings.early.color);
        } else {
            td.style.backgroundColor = settings.late.color;
            console.log('Applied late color:', settings.late.color);
        }
        
        // Handle overnight shifts
        if (startTotalMinutes > endTotalMinutes && !td.style.backgroundColor) {
            if (startTotalMinutes < night_shift) {
                td.style.backgroundColor = settings.late.color;
                console.log('Applied late color (overnight):', settings.late.color);
            }
        }
    }

    applyDayOffColors(td, times, settings) {
        const listOfDaysoff = ['XX', 'OO', 'TT', ''];
        if (listOfDaysoff.includes(times[0])) {
            td.style.backgroundColor = settings.dayoff.color;
            console.log('Applied day off color:', settings.dayoff.color);
        }
    }

    initializeColorInputs() {
        const settings = this.loadColorSettings();
        
        try {
            // Set color values
            const colorInputs = {
                'early-color': settings.early.color,
                'late-color': settings.late.color,
                'night-color': settings.night.color,
                'dayoff-color': settings.dayoff.color,
                'hdag-color': settings.hdag.color,
                'earlylate-color': settings.earlylate.color
            };

            Object.entries(colorInputs).forEach(([id, value]) => {
                const input = document.getElementById(id);
                if (input) input.value = value;
            });
            
            // Set time values
            const timeInputs = {
                'early-time': settings.early.time,
                'late-time': settings.late.time,
                'night-time': settings.night.time
            };

            Object.entries(timeInputs).forEach(([id, value]) => {
                const input = document.getElementById(id);
                if (input) input.value = value;
            });
            
            console.log('Color inputs initialized with settings:', settings);
        } catch (error) {
            console.error('Error initializing color inputs:', error);
        }
    }

    handleApplyColors() {
        try {
            const newSettings = {
                early: {
                    color: document.getElementById('early-color')?.value || this.defaultSettings.early.color,
                    time: document.getElementById('early-time')?.value || this.defaultSettings.early.time
                },
                late: {
                    color: document.getElementById('late-color')?.value || this.defaultSettings.late.color,
                    time: document.getElementById('late-time')?.value || this.defaultSettings.late.time
                },
                night: {
                    color: document.getElementById('night-color')?.value || this.defaultSettings.night.color,
                    time: document.getElementById('night-time')?.value || this.defaultSettings.night.time
                },
                dayoff: {
                    color: document.getElementById('dayoff-color')?.value || this.defaultSettings.dayoff.color
                },
                hdag: {
                    color: document.getElementById('hdag-color')?.value || this.defaultSettings.hdag.color
                },
                earlylate: {
                    color: document.getElementById('earlylate-color')?.value || this.defaultSettings.earlylate.color
                }
            };

            this.saveColorSettings(newSettings);
            this.applyColorsToTable();
            
            this.showButtonFeedback('apply-colors', 'Farger brukt!', 'btn-success');
            console.log('Colors applied successfully');
        } catch (error) {
            console.error('Error applying colors:', error);
            alert('Feil ved bruk av farger. Sjekk konsollen for detaljer.');
        }
    }

    handleResetColors() {
        if (confirm('Er du sikker på at du vil tilbakestille alle fargeinnstillinger?')) {
            try {
                localStorage.removeItem('shiftColorSettings');
                this.initializeColorInputs();
                this.applyColorsToTable();
                
                this.showButtonFeedback('reset-colors', 'Reset!', 'btn-success');
                console.log('Colors reset to defaults');
            } catch (error) {
                console.error('Error resetting colors:', error);
                alert('Feil ved tilbakestilling av farger. Sjekk konsollen for detaljer.');
            }
        }
    }

    showButtonFeedback(buttonId, message, successClass) {
        const button = document.getElementById(buttonId);
        if (!button) return;

        const originalText = button.innerHTML;
        const originalClass = button.className;
        
        button.innerHTML = `<i class="bi bi-check-circle-fill"></i> ${message}`;
        button.className = button.className.replace(/btn-\w+/, successClass);
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.className = originalClass;
        }, 2000);
    }
}
