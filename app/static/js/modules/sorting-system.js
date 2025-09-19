// Sorting System Module
// Handles turnusliste sorting functionality

export class SortingSystem {
    constructor() {
        console.log('SortingSystem module initializing...');
        this.originalOrder = [];
        this.currentOrder = [];
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeSorting();
            });
        } else {
            this.initializeSorting();
        }
    }

    initializeSorting() {
        // Check if we're on the turnusliste page
        const sortingContainer = document.querySelector('#helgetimer-slider');
        if (!sortingContainer) {
            console.log('No sorting container found, skipping sorting initialization');
            return;
        }

        console.log('Initializing sorting system...');
        this.initializeOriginalOrder();
        this.setupEventListeners();
        
        // Load and apply saved settings, then sort if any were applied
        if (this.applySavedSettings()) {
            this.sortTurnuser();
        }
        
        // Initialize slider values
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => this.updateSliderValue(slider));
    }

    initializeOriginalOrder() {
        const turnusItems = document.querySelectorAll('.list-group-item');
        this.originalOrder = Array.from(turnusItems).map(item => {
            const turnusName = item.querySelector('.t-name').textContent.trim();
            return { element: item, name: turnusName };
        });
        this.currentOrder = [...this.originalOrder];
        console.log(`Initialized original order with ${this.originalOrder.length} items`);
    }

    getTurnusData() {
        const turnusData = [];
        const turnusItems = document.querySelectorAll('.list-group-item');
        
        console.log('Found turnus items:', turnusItems.length);
        
        turnusItems.forEach((item, index) => {
            const turnusName = item.querySelector('.t-name');
            if (!turnusName) {
                console.warn(`No turnus name found for item ${index}`);
                return;
            }
            
            const name = turnusName.textContent.trim();
            const dataRow = item.querySelector('.data-felt');
            
            if (dataRow) {
                try {
                    // First row: Dagsverk, Tidlig, Kveld, Natt
                    const shiftCnt = parseInt(dataRow.querySelector('.row:nth-child(1) .col:nth-child(1) b').textContent) || 0;
                    const tidlig = parseInt(dataRow.querySelector('.row:nth-child(1) .col:nth-child(2) b').textContent) || 0;
                    const ettermiddag = parseInt(dataRow.querySelector('.row:nth-child(1) .col:nth-child(3) b').textContent) || 0;
                    const natt = parseInt(dataRow.querySelector('.row:nth-child(1) .col:nth-child(4) b').textContent) || 0;
                    
                    // Second row: Helgetimer, Helgtimer dag, Starter før 6, Slutt før 20
                    const helgetimer = parseInt(dataRow.querySelector('.row:nth-child(2) .col:nth-child(1) b').textContent) || 0;
                    const before6 = parseInt(dataRow.querySelector('.row:nth-child(2) .col:nth-child(3) b').textContent) || 0;
                    const afternoonEnds = parseInt(dataRow.querySelector('.row:nth-child(2) .col:nth-child(4) b').textContent) || 0;
                    
                    console.log(`Turnus ${name}:`, { shiftCnt, tidlig, ettermiddag, natt, helgetimer, before6, afternoonEnds });
                    
                    turnusData.push({
                        name: name,
                        element: item,
                        shift_cnt: shiftCnt,
                        tidlig: tidlig,
                        ettermiddag: ettermiddag,
                        natt: natt,
                        helgetimer: helgetimer,
                        before_6: before6,
                        afternoon_ends_before_20: afternoonEnds
                    });
                } catch (error) {
                    console.error(`Error parsing data for turnus ${name}:`, error);
                }
            } else {
                console.warn(`No data-felt found for turnus ${name}`);
            }
        });
        
        console.log('Total turnus data collected:', turnusData.length);
        return turnusData;
    }

    calculateScore(turnus, weights) {
        let score = 0;
        
        // For each criteria, calculate contribution based on weight direction and magnitude
        Object.entries(weights).forEach(([key, weight]) => {
            if (weight === 0) return; // Skip neutral weights
            
            let value = 0;
            switch(key) {
                case 'helgetimer': value = turnus.helgetimer; break;
                case 'shift_cnt': value = turnus.shift_cnt; break;
                case 'tidlig': value = turnus.tidlig; break;
                case 'natt': value = turnus.natt; break;
                case 'ettermiddag': value = turnus.ettermiddag; break;
                case 'before_6': value = turnus.before_6; break;
                case 'afternoon_ends': value = turnus.afternoon_ends_before_20; break;
            }
            
            // Calculate contribution: weight magnitude determines priority
            // Positive weight: higher values get higher scores
            // Negative weight: lower values get higher scores
            let contribution;
            if (weight > 0) {
                contribution = value * Math.abs(weight);
            } else {
                // For negative weights, invert the value so lower values get higher scores
                // Use max possible value to create proper inversion
                const maxValue = this.getMaxValueForCriteria(key);
                contribution = (maxValue - value) * Math.abs(weight);
            }
            
            score += contribution;
        });
        
        return score;
    }

    getMaxValueForCriteria(criteria) {
        // These are reasonable maximum values based on typical turnus data
        const maxValues = {
            helgetimer: 50,        // Max weekend hours
            shift_cnt: 30,         // Max work days
            tidlig: 20,            // Max early shifts
            natt: 20,              // Max night shifts
            ettermiddag: 20,       // Max afternoon shifts
            before_6: 20,          // Max shifts before 6
            afternoon_ends: 20     // Max shifts ending before 20
        };
        return maxValues[criteria] || 50;
    }

    sortTurnuser() {
        const weights = {
            helgetimer: parseFloat(document.getElementById('helgetimer-slider').value),
            shift_cnt: parseFloat(document.getElementById('shift-cnt-slider').value),
            tidlig: parseFloat(document.getElementById('tidlig-slider').value),
            natt: parseFloat(document.getElementById('natt-slider').value),
            ettermiddag: parseFloat(document.getElementById('ettermiddag-slider').value),
            before_6: parseFloat(document.getElementById('before-6-slider').value),
            afternoon_ends: parseFloat(document.getElementById('afternoon-ends-slider').value)
        };
        
        const turnusData = this.getTurnusData();
        
        if (turnusData.length === 0) {
            console.warn('No turnus data found');
            return;
        }
        
        // Calculate scores and sort
        turnusData.forEach(turnus => {
            turnus.score = this.calculateScore(turnus, weights);
        });
        
        turnusData.sort((a, b) => b.score - a.score);
        
        // Reorder DOM elements
        const container = document.querySelector('.list-group');
        if (container) {
            turnusData.forEach(turnus => {
                container.appendChild(turnus.element);
            });
        }
        
        // Update current order
        this.currentOrder = turnusData.map(t => ({ element: t.element, name: t.name }));
        
        // Update sorting info display
        this.updateSortingInfo(weights);
    }

    resetOrder() {
        const container = document.querySelector('.list-group');
        this.originalOrder.forEach(turnus => {
            container.appendChild(turnus.element);
        });
        this.currentOrder = [...this.originalOrder];
        
        // Reset all sliders
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.value = 0;
            this.updateSliderValue(slider);
        });
        
        // Clear saved settings
        try {
            localStorage.removeItem('turnuslisteSortingSettings');
            console.log('Sorting settings cleared');
        } catch (error) {
            console.error('Error clearing sorting settings:', error);
        }
        
        // Hide sorting info
        const sortingInfo = document.getElementById('sorting-info');
        if (sortingInfo) {
            sortingInfo.style.display = 'none';
        }
    }

    updateSliderValue(slider) {
        const valueDisplay = document.getElementById(slider.id.replace('-slider', '-value'));
        if (valueDisplay) {
            valueDisplay.textContent = slider.value;
            
            // Update badge color based on value
            if (parseFloat(slider.value) > 0) {
                valueDisplay.className = 'badge bg-success';
            } else if (parseFloat(slider.value) < 0) {
                valueDisplay.className = 'badge bg-secondary';
            } else {
                valueDisplay.className = 'badge bg-secondary';
            }
        }
        
        // Set data-value attribute for inline display
        slider.setAttribute('data-value', slider.value);
    }

    updateSortingInfo(weights) {
        const sortingInfo = document.getElementById('sorting-info');
        const sortingCriteria = document.getElementById('sorting-criteria');
        
        if (!sortingInfo || !sortingCriteria) return;
        
        const activeCriteria = [];
        Object.entries(weights).forEach(([key, value]) => {
            if (value !== 0) {
                const label = this.getCriteriaLabel(key);
                const direction = value > 0 ? 'Høy → Lav' : 'Lav → Høy';
                activeCriteria.push(`${label}: ${direction}`);
            }
        });
        
        if (activeCriteria.length > 0) {
            sortingCriteria.textContent = activeCriteria.join(', ');
            sortingInfo.style.display = 'block';
        } else {
            sortingInfo.style.display = 'none';
        }
    }

    getCriteriaLabel(key) {
        const labels = {
            helgetimer: 'Helgetimer',
            shift_cnt: 'Dagsverk',
            tidlig: 'Tidlig',
            natt: 'Natt',
            ettermiddag: 'Ettermiddag',
            before_6: 'Før 6:00',
            afternoon_ends: 'Slutt før 20:00'
        };
        return labels[key] || key;
    }

    saveSortingSettings() {
        try {
            const settings = {
                helgetimer: document.getElementById('helgetimer-slider').value,
                shift_cnt: document.getElementById('shift-cnt-slider').value,
                tidlig: document.getElementById('tidlig-slider').value,
                natt: document.getElementById('natt-slider').value,
                ettermiddag: document.getElementById('ettermiddag-slider').value,
                before_6: document.getElementById('before-6-slider').value,
                afternoon_ends: document.getElementById('afternoon-ends-slider').value
            };
            localStorage.setItem('turnuslisteSortingSettings', JSON.stringify(settings));
            console.log('Sorting settings saved:', settings);
        } catch (error) {
            console.error('Error saving sorting settings:', error);
        }
    }

    loadSortingSettings() {
        try {
            const saved = localStorage.getItem('turnuslisteSortingSettings');
            if (saved) {
                const settings = JSON.parse(saved);
                console.log('Loading sorting settings:', settings);
                return settings;
            }
        } catch (error) {
            console.warn('Error loading sorting settings:', error);
        }
        return null;
    }

    applySavedSettings() {
        const settings = this.loadSortingSettings();
        if (!settings) return false;

        let anySettingsApplied = false;
        
        // Apply to desktop sliders
        Object.entries(settings).forEach(([key, value]) => {
            const sliderId = key === 'shift_cnt' ? 'shift-cnt-slider' : 
                           key === 'before_6' ? 'before-6-slider' :
                           key === 'afternoon_ends' ? 'afternoon-ends-slider' :
                           `${key}-slider`;
            
            const slider = document.getElementById(sliderId);
            const mobileSlider = document.getElementById(sliderId + '-mobile');
            
            if (slider && value !== undefined && value !== '0') {
                slider.value = value;
                this.updateSliderValue(slider);
                anySettingsApplied = true;
            }
            
            if (mobileSlider && value !== undefined && value !== '0') {
                mobileSlider.value = value;
                this.updateSliderValue(mobileSlider);
            }
        });

        return anySettingsApplied;
    }

    setupEventListeners() {
        // Add event listeners to sliders (both desktop and mobile filters)
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            // Set initial value display
            this.updateSliderValue(slider);
            
            slider.addEventListener('input', () => {
                this.updateSliderValue(slider);
                
                // Sync mobile and desktop sliders
                const sliderId = slider.id;
                if (sliderId.includes('-mobile')) {
                    const desktopId = sliderId.replace('-mobile', '');
                    const desktopSlider = document.getElementById(desktopId);
                    if (desktopSlider) {
                        desktopSlider.value = slider.value;
                        this.updateSliderValue(desktopSlider);
                    }
                } else {
                    const mobileId = sliderId + '-mobile';
                    const mobileSlider = document.getElementById(mobileId);
                    if (mobileSlider) {
                        mobileSlider.value = slider.value;
                        this.updateSliderValue(mobileSlider);
                    }
                }
                
                this.sortTurnuser();
                this.saveSortingSettings(); // Save settings after each change
            });
        });
        
        // Add event listener to reset buttons (both desktop and mobile)
        const resetButtons = document.querySelectorAll('#reset-sorting, #reset-sorting-mobile');
        resetButtons.forEach(button => {
            button.addEventListener('click', () => this.resetOrder());
        });

        // Make hideSortingInfo available globally for backward compatibility
        window.hideSortingInfo = () => {
            const sortingInfo = document.getElementById('sorting-info');
            if (sortingInfo) {
                sortingInfo.style.display = 'none';
            }
        };
    }
}
