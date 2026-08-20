// Sorting System Module
// Handles turnusliste sorting functionality

export class SortingSystem {
    constructor() {
        this.originalOrder = [];
        this.currentOrder = [];
        this.metrics = {};
        this.saveTimer = null;
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

        this.metrics = this.loadMetrics();
        this.initializeOriginalOrder();
        this.setupEventListeners();
        
        // Load and apply saved settings, then sort if any were applied
        if (this.applySavedSettings()) {
            this.sortTurnuser();
        }
        
        // Initialize slider values
        const sliders = document.querySelectorAll('.filter-slider');
        sliders.forEach(slider => this.updateSliderValue(slider));
    }

    /**
     * Real numbers from the route, keyed by raw turnus name.
     *
     * This replaced parsing the rendered .data-felt grid, which read every value
     * through parseInt on a positional <b> index: helgetimer 58.3 became 58, an
     * unknown kompdager count ("–") became 0 — i.e. the best rank under "Færre" —
     * and reordering one cell in the grid silently mis-mapped every field after it.
     */
    loadMetrics() {
        const block = document.getElementById('turnus-metrics');
        if (!block) {
            console.warn('No #turnus-metrics block found; sorting will be neutral');
            return {};
        }
        try {
            return JSON.parse(block.textContent) || {};
        } catch (error) {
            console.error('Could not parse #turnus-metrics:', error);
            return {};
        }
    }

    /**
     * The turnus cards, paired with their raw name.
     *
     * Identity comes from data-turnus, never from .t-name — that goes through the
     * display_name filter, so it reads "OSL 01" while the metrics are keyed
     * "OSL_01". Cards without the attribute are skipped rather than sorted blind.
     */
    getTurnusItems() {
        const items = document.querySelectorAll('.list-group-item[data-turnus]');
        return Array.from(items).map(element => ({
            element,
            name: element.dataset.turnus
        }));
    }

    initializeOriginalOrder() {
        this.originalOrder = this.getTurnusItems();
        this.currentOrder = [...this.originalOrder];
    }

    getTurnusData() {
        return this.getTurnusItems().map(({ element, name }) => {
            const metrics = this.metrics[name];
            if (!metrics) {
                // Still take part in the sort, with every criterion unknown —
                // otherwise appendChild never touches this card and it sits still
                // while the rest of the list reorders around it.
                console.warn(`No metrics for turnus ${name}`);
            }
            return { name, element, ...(metrics || {}) };
        });
    }

    /**
     * Calculate min/max values for each criterion from the current dataset
     */
    calculateMinMax(turnusData) {
        const criteria = ['helgetimer', 'helgetimer_dagtid', 'helgetimer_ettermiddag', 'helgetimer_natt',
                          'shift_cnt', 'tidlig', 'natt', 'ettermiddag', 'before_6',
                          'tidlig_6_8', 'tidlig_8_12', 'longest_off_streak', 'longest_work_streak', 'kompdager_max'];
        const minMax = {};

        criteria.forEach(key => {
            // == null catches both null (unknown, e.g. kompdager without the
            // nøkkel template) and undefined. A falsy test would swallow a
            // legitimate 0 — which is exactly what the old `|| 0` did.
            const values = turnusData
                .map(t => t[key])
                .filter(value => value != null);

            minMax[key] = values.length
                ? { min: Math.min(...values), max: Math.max(...values) }
                : { min: 0, max: 1 };
        });

        return minMax;
    }

    /**
     * Normalize a value to a 0-1 scale based on min/max
     */
    normalizeValue(value, min, max) {
        if (max === min) return 0.5; // Avoid division by zero
        return (value - min) / (max - min);
    }

    calculateScore(turnus, weights, minMax) {
        let score = 0;

        // For each criteria, calculate contribution based on normalized values and weights
        Object.entries(weights).forEach(([key, weight]) => {
            if (weight === 0) return; // Skip neutral weights

            const dataKey = key;
            const value = turnus[dataKey];
            const { min, max } = minMax[dataKey] || { min: 0, max: 1 };

            // Unknown is neutral, not zero. Scoring it as 0 would rank a turnus
            // with no kompdag data as having the fewest of them. Note 0.5 lands
            // the same contribution whichever sign the weight has.
            const normalized = value == null
                ? 0.5
                : this.normalizeValue(value, min, max);

            // Positive weight: higher normalized values get higher scores
            // Negative weight: lower normalized values get higher scores (invert)
            let contribution;
            if (weight > 0) {
                contribution = normalized * Math.abs(weight);
            } else {
                contribution = (1 - normalized) * Math.abs(weight);
            }

            score += contribution;
        });

        return score;
    }

    sortTurnuser() {
        const weights = {
            helgetimer: parseFloat(document.getElementById('helgetimer-slider').value),
            helgetimer_dagtid: parseFloat(document.getElementById('helgetimer-dagtid-slider').value),
            helgetimer_ettermiddag: parseFloat(document.getElementById('helgetimer-ettermiddag-slider').value),
            helgetimer_natt: parseFloat(document.getElementById('helgetimer-natt-slider').value),
            shift_cnt: parseFloat(document.getElementById('shift-cnt-slider').value),
            tidlig: parseFloat(document.getElementById('tidlig-slider').value),
            natt: parseFloat(document.getElementById('natt-slider').value),
            ettermiddag: parseFloat(document.getElementById('ettermiddag-slider').value),
            before_6: parseFloat(document.getElementById('before-6-slider').value),
            tidlig_6_8: parseFloat(document.getElementById('tidlig-6-8-slider').value),
            tidlig_8_12: parseFloat(document.getElementById('tidlig-8-12-slider').value),
            longest_off_streak: parseFloat(document.getElementById('longest-off-slider').value),
            longest_work_streak: parseFloat(document.getElementById('longest-streak-slider').value),
            kompdager_max: parseFloat(document.getElementById('kompdager-slider').value)
        };

        const turnusData = this.getTurnusData();

        if (turnusData.length === 0) {
            console.warn('No turnus data found');
            return;
        }

        // Calculate actual min/max from data for normalization
        const minMax = this.calculateMinMax(turnusData);

        // Calculate scores with normalization
        turnusData.forEach(turnus => {
            turnus.score = this.calculateScore(turnus, weights, minMax);
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
        this.updateMatchBadges(turnusData, weights);
        this.updateSortingInfo(weights);
    }

    /**
     * Per-card "NN %" — the share of the maximum achievable score.
     *
     * Values are min/max-normalised across the rendered list, so this is a
     * comparison against the other turnuser, not an absolute quality score: with
     * one active slider the top card always reads 100 % and the bottom 0 %, and
     * if every value is identical they all read 50 %. The title and the panel
     * hint say so — a bare "100 %" reads as "perfect match".
     */
    updateMatchBadges(turnusData, weights) {
        const totalWeight = Object.values(weights)
            .reduce((sum, weight) => sum + Math.abs(weight), 0);

        if (totalWeight === 0) {
            this.clearMatchBadges();
            return;
        }

        const criteria = this.activeCriteria(weights).join(', ');

        turnusData.forEach(turnus => {
            const badge = turnus.element.querySelector('.turnus-match-badge');
            if (!badge) return;

            badge.textContent = `${Math.round((turnus.score / totalWeight) * 100)} %`;
            badge.title = `Treff sammenlignet med de andre turnusene i lista. Kriterier: ${criteria}`;
            badge.classList.remove('d-none');
        });
    }

    clearMatchBadges() {
        document.querySelectorAll('.turnus-match-badge').forEach(badge => {
            badge.textContent = '';
            badge.title = '';
            badge.classList.add('d-none');
        });
    }

    resetOrder() {
        const container = document.querySelector('.list-group');
        this.originalOrder.forEach(turnus => {
            container.appendChild(turnus.element);
        });
        this.currentOrder = [...this.originalOrder];
        
        // Reset all sliders
        const sliders = document.querySelectorAll('.filter-slider');
        sliders.forEach(slider => {
            slider.value = 0;
            this.updateSliderValue(slider);
        });
        
        // Drop any pending debounced write first — otherwise a timer armed by the
        // drag that preceded this click fires afterwards and writes the weights
        // we just cleared straight back into localStorage.
        this.cancelPendingSave();

        // Clear saved settings
        try {
            localStorage.removeItem('turnuslisteSortingSettings');
            console.log('Sorting settings cleared');
        } catch (error) {
            console.error('Error clearing sorting settings:', error);
        }

        // This path never calls sortTurnuser(), so the per-card match badges have
        // to be cleared here too, not only in its zero-weight branch.
        this.clearMatchBadges();

        // Clear active-criteria badge on the Sorter button
        const badge = document.getElementById('sorter-active-badge');
        if (badge) {
            badge.textContent = '0';
            badge.classList.add('d-none');
            badge.title = '';
        }
    }

    updateSliderValue(slider) {
        const value = parseFloat(slider.value) || 0;
        const min = parseFloat(slider.min);
        const max = parseFloat(slider.max);

        // Show the number only when the slider is off centre — eleven zeroes
        // carry no information.
        const valueDisplay = document.getElementById(slider.id.replace('-slider', '-value'));
        if (valueDisplay) {
            valueDisplay.textContent = value === 0 ? '' : (value > 0 ? `+${value}` : `${value}`);
        }

        // Percentages the CSS fill is painted between: the neutral point and the
        // thumb, in whichever order puts the smaller first.
        const neutral = ((0 - min) / (max - min)) * 100;
        const current = ((value - min) / (max - min)) * 100;
        slider.style.setProperty('--fill-start', `${Math.min(neutral, current)}%`);
        slider.style.setProperty('--fill-end', `${Math.max(neutral, current)}%`);

        const item = slider.closest('.filter-item');
        if (item) {
            item.classList.toggle('is-active', value !== 0);
        }
    }

    /** Labelled criteria the user has actually moved, e.g. "Natt: Lav → Høy". */
    activeCriteria(weights) {
        return Object.entries(weights)
            .filter(([, value]) => value !== 0)
            .map(([key, value]) => {
                const direction = value > 0 ? 'Høy → Lav' : 'Lav → Høy';
                return `${this.getCriteriaLabel(key)}: ${direction}`;
            });
    }

    updateSortingInfo(weights) {
        const activeCriteria = this.activeCriteria(weights);

        const badge = document.getElementById('sorter-active-badge');
        if (badge) {
            badge.textContent = activeCriteria.length;
            badge.classList.toggle('d-none', activeCriteria.length === 0);
            badge.title = activeCriteria.join(', ');
        }
    }

    getCriteriaLabel(key) {
        const labels = {
            helgetimer: 'Helgetimer',
            helgetimer_dagtid: 'Helg dagtid',
            helgetimer_ettermiddag: 'Helg kveld',
            helgetimer_natt: 'Helg natt',
            shift_cnt: 'Dagsverk',
            tidlig: 'Tidlig',
            natt: 'Natt',
            ettermiddag: 'Ettermiddag',
            before_6: 'Før 6:00',
            tidlig_6_8: 'Tidlig 6-8',
            tidlig_8_12: 'Tidlig 8-12',
            longest_off_streak: 'Lengste fri',
            longest_work_streak: 'Lengste rekke',
            kompdager_max: 'Kompdager (maks)'
        };
        return labels[key] || key;
    }

    /**
     * Defer the write. 'input' fires continuously while a slider is dragged; the
     * sort stays synchronous per event because the immediate reorder is the whole
     * point, but localStorage only needs the value the user settles on.
     */
    queueSaveSortingSettings() {
        this.cancelPendingSave();
        this.saveTimer = window.setTimeout(() => {
            this.saveTimer = null;
            this.saveSortingSettings();
        }, 200);
    }

    cancelPendingSave() {
        if (this.saveTimer !== null) {
            window.clearTimeout(this.saveTimer);
            this.saveTimer = null;
        }
    }

    saveSortingSettings() {
        try {
            const settings = {
                helgetimer: document.getElementById('helgetimer-slider').value,
                helgetimer_dagtid: document.getElementById('helgetimer-dagtid-slider').value,
                helgetimer_ettermiddag: document.getElementById('helgetimer-ettermiddag-slider').value,
                helgetimer_natt: document.getElementById('helgetimer-natt-slider').value,
                shift_cnt: document.getElementById('shift-cnt-slider').value,
                tidlig: document.getElementById('tidlig-slider').value,
                natt: document.getElementById('natt-slider').value,
                ettermiddag: document.getElementById('ettermiddag-slider').value,
                before_6: document.getElementById('before-6-slider').value,
                tidlig_6_8: document.getElementById('tidlig-6-8-slider').value,
                tidlig_8_12: document.getElementById('tidlig-8-12-slider').value,
                longest_off_streak: document.getElementById('longest-off-slider').value,
                longest_work_streak: document.getElementById('longest-streak-slider').value,
                kompdager_max: document.getElementById('kompdager-slider').value
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
                           key === 'tidlig_6_8' ? 'tidlig-6-8-slider' :
                           key === 'tidlig_8_12' ? 'tidlig-8-12-slider' :
                           key === 'longest_off_streak' ? 'longest-off-slider' :
                           key === 'longest_work_streak' ? 'longest-streak-slider' :
                           key === 'kompdager_max' ? 'kompdager-slider' :
                           // Everything else: the metric key with underscores
                           // swapped for hyphens. The branches above are the
                           // irregular ones, whose id is not derivable.
                           `${key.replace(/_/g, '-')}-slider`;
            
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
        const sliders = document.querySelectorAll('.filter-slider');
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
                this.queueSaveSortingSettings();
            });
        });
        
        // Add event listener to reset buttons (both desktop and mobile)
        const resetButtons = document.querySelectorAll('#reset-sorting, #reset-sorting-mobile');
        resetButtons.forEach(button => {
            button.addEventListener('click', () => this.resetOrder());
        });

        // The panel uses data-bs-auto-close="outside", so nothing inside it closes
        // the dropdown. Ferdig has to do it explicitly — a data-bs-toggle here
        // would be a no-op, since Bootstrap resolves a toggle's menu from its
        // sibling and this button sits inside the menu.
        const doneButton = document.getElementById('sorter-done');
        if (doneButton) {
            doneButton.addEventListener('click', () => {
                const toggle = document.querySelector('.navbar-filtering .sorter-btn');
                if (toggle && window.bootstrap) {
                    window.bootstrap.Dropdown.getOrCreateInstance(toggle).hide();
                }
            });
        }

        // Fix aria-hidden warning: blur any focused element inside the modal before it hides
        const modal = document.getElementById('mobileSorterModal');
        if (modal) {
            modal.addEventListener('hide.bs.modal', () => {
                const focused = modal.querySelector(':focus');
                if (focused) focused.blur();
            });
        }
    }
}
