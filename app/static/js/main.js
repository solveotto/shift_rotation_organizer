// Main JavaScript entry point
// Coordinates all modules and handles initialization

import { ShiftSelection } from './modules/shift-selection.js';
import { ShiftColors } from './modules/shift-colors.js';
import { SortingSystem } from './modules/sorting-system.js';
import { Favorites } from './modules/favorites.js';
import { PrintUtils } from './modules/print-utils.js';

// NOT USED
// import { Utils, ScrollPosition } from './modules/utils.js';
// import { ColorAdjustment } from './modules/color-adjustment.js';

class App {
    constructor() {
        this.modules = {};
        this.init();
    }

    init() {
        // Initialize modules based on page context
        this.initializeModules();
    }

    initializeModules() {
        // Always initialize these modules
        this.modules.favorites = new Favorites();
        // this.modules.scrollPosition = new ScrollPosition(); // Disabled - Utils not imported

        // Initialize shift colors if we have table cells (applies CSS classes)
        if (document.querySelector('td[id="cell"]')) {
            console.log('Table cells found, initializing ShiftColors...');
            this.modules.shiftColors = new ShiftColors();
        } else {
            console.log('No table cells found (td[id="cell"]), skipping ShiftColors');
        }

        // Initialize shift selection if we have clickable rows
        if (document.querySelector('.clickable-row')) {
            this.modules.shiftSelection = new ShiftSelection();
        }

        // Initialize color adjustment if we're on the turnusliste page (user customization UI)
        // Note: ColorAdjustment module is commented out - uncomment import above to re-enable
        // if (document.querySelector('#apply-colors')) {
        //     this.modules.colorAdjustment = new ColorAdjustment();
        // }

        // Initialize sorting if we're on the turnusliste page
        if (document.querySelector('#helgetimer-slider')) {
            console.log('Sorting controls found, initializing SortingSystem...');
            this.modules.sorting = new SortingSystem();
        }

        console.log('App initialized with modules:', Object.keys(this.modules));
    }

    getModule(name) {
        return this.modules[name];
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});

// Export for potential external access
export default App;
