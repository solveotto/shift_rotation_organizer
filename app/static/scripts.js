
// Makes shifts checkbox in the index-page clickable
document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', () => {
            const turnus = row.getAttribute('data-turnus');

                console.log('Turnus:', turnus);
            

            fetch('/api/js_select_shift', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ shift_title: turnus })
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        });
   
    });
        // Add click event listener to checkboxes to stop propagation
        document.querySelectorAll('.prevent-click').forEach(checkbox => {
            checkbox.addEventListener('click', function(event) {
                event.stopPropagation();
            });
        });
});

// Color adjustment system
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the turnusliste page
    const colorPanel = document.querySelector('#apply-colors');
    if (!colorPanel) return;

    // Default color and time settings
    const defaultSettings = {
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

    // Load saved settings from localStorage or use defaults
    function loadColorSettings() {
        try {
            const saved = localStorage.getItem('shiftColorSettings');
            if (saved) {
                return { ...defaultSettings, ...JSON.parse(saved) };
            }
        } catch (error) {
            console.warn('Error loading color settings:', error);
        }
        return defaultSettings;
    }

    // Save settings to localStorage
    function saveColorSettings(settings) {
        try {
            localStorage.setItem('shiftColorSettings', JSON.stringify(settings));
            console.log('Color settings saved:', settings);
        } catch (error) {
            console.error('Error saving color settings:', error);
        }
    }

    // Apply colors to the shift table
    function applyColorsToTable() {
        const settings = loadColorSettings();
        console.log('Applying colors with settings:', settings);
        
        // Remove existing color classes
        const tds = document.querySelectorAll('td[id="cell"]');
        console.log(`Found ${tds.length} table cells to color`);
        
        tds.forEach(td => {
            td.classList.remove('early', 'late', 'night', 'day_off', 'h-dag', 'early-and-late');
            td.style.backgroundColor = '';
            td.style.color = '';
        });

        // Apply new colors based on settings
        tds.forEach(td => {
            const timeTextElement = td.querySelector('.time-text');
            if (timeTextElement) {
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

                    // Apply colors based on new thresholds
                    // Check night shift first (highest priority)
                    if (startTotalMinutes >= night_shift) {
                        td.style.backgroundColor = settings.night.color;
                        console.log('Applied night color:', settings.night.color, 'for time:', timeText, 'start:', startTime, 'startTotalMinutes:', startTotalMinutes, 'night_shift:', night_shift);
                    }
                    // Check early + late shift combination
                    else if (start_hours > 5 && start_hours < 9 && end_hours >= 16 && end_hours < 18) {
                        td.style.backgroundColor = settings.earlylate.color;
                        td.style.color = 'white';
                        console.log('Applied early+late color:', settings.earlylate.color, 'for time:', timeText);
                    }
                    // Check early vs late shifts
                    else if (endTotalMinutes <= late_shift) {
                        td.style.backgroundColor = settings.early.color;
                        console.log('Applied early color:', settings.early.color, 'for time:', timeText);
                    } else {
                        td.style.backgroundColor = settings.late.color;
                        console.log('Applied late color:', settings.late.color, 'for time:', timeText);
                    }
                    
                    // Handle overnight shifts (start time > end time) - only if not already colored
                    if (startTotalMinutes > endTotalMinutes && !td.style.backgroundColor) {
                        // If it's not already a night shift, apply late color
                        if (startTotalMinutes < night_shift) {
                            td.style.backgroundColor = settings.late.color;
                            console.log('Applied late color (overnight):', settings.late.color, 'for time:', timeText);
                        }
                    }

                } else {
                    const listOfDaysoff = ['XX', 'OO', 'TT', ''];
                    if (listOfDaysoff.includes(times[0])) {
                        td.style.backgroundColor = settings.dayoff.color;
                        console.log('Applied day off color:', settings.dayoff.color, 'for text:', times[0]);
                    }
                }
            }
        });
        
        console.log('Color application completed');
    }

    // Initialize color inputs with current settings
    function initializeColorInputs() {
        const settings = loadColorSettings();
        
        try {
            // Set color values
            const earlyColor = document.getElementById('early-color');
            const lateColor = document.getElementById('late-color');
            const nightColor = document.getElementById('night-color');
            const dayoffColor = document.getElementById('dayoff-color');
            const hdagColor = document.getElementById('hdag-color');
            const earlylateColor = document.getElementById('earlylate-color');
            
            if (earlyColor) earlyColor.value = settings.early.color;
            if (lateColor) lateColor.value = settings.late.color;
            if (nightColor) nightColor.value = settings.night.color;
            if (dayoffColor) dayoffColor.value = settings.dayoff.color;
            if (hdagColor) hdagColor.value = settings.hdag.color;
            if (earlylateColor) earlylateColor.value = settings.earlylate.color;
            
            // Set time values
            const earlyTime = document.getElementById('early-time');
            const lateTime = document.getElementById('late-time');
            const nightTime = document.getElementById('night-time');
            
            if (earlyTime) earlyTime.value = settings.early.time;
            if (lateTime) lateTime.value = settings.late.time;
            if (nightTime) nightTime.value = settings.night.time;
            
            console.log('Color inputs initialized with settings:', settings);
        } catch (error) {
            console.error('Error initializing color inputs:', error);
        }
    }

    // Apply button click handler
    const applyButton = document.getElementById('apply-colors');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            try {
                const newSettings = {
                    early: {
                        color: document.getElementById('early-color')?.value || defaultSettings.early.color,
                        time: document.getElementById('early-time')?.value || defaultSettings.early.time
                    },
                    late: {
                        color: document.getElementById('late-color')?.value || defaultSettings.late.color,
                        time: document.getElementById('late-time')?.value || defaultSettings.late.time
                    },
                    night: {
                        color: document.getElementById('night-color')?.value || defaultSettings.night.color,
                        time: document.getElementById('night-time')?.value || defaultSettings.night.time
                    },
                    dayoff: {
                        color: document.getElementById('dayoff-color')?.value || defaultSettings.dayoff.color
                    },
                    hdag: {
                        color: document.getElementById('hdag-color')?.value || defaultSettings.hdag.color
                    },
                    earlylate: {
                        color: document.getElementById('earlylate-color')?.value || defaultSettings.earlylate.color
                    }
                };

                saveColorSettings(newSettings);
                applyColorsToTable();
                
                // Show success feedback
                const button = this;
                const originalText = button.innerHTML;
                button.innerHTML = '<i class="bi bi-check-circle-fill"></i> Farger brukt!';
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-success');
                
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('btn-success');
                    button.classList.add('btn-outline-primary');
                }, 2000);
                
                console.log('Colors applied successfully');
            } catch (error) {
                console.error('Error applying colors:', error);
                alert('Feil ved bruk av farger. Sjekk konsollen for detaljer.');
            }
        });
    }

    // Reset button click handler
    const resetButton = document.getElementById('reset-colors');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            if (confirm('Er du sikker på at du vil tilbakestille alle fargeinnstillinger?')) {
                try {
                    localStorage.removeItem('shiftColorSettings');
                    initializeColorInputs();
                    applyColorsToTable();
                    
                    // Show reset feedback
                    const button = this;
                    const originalText = button.innerHTML;
                    button.innerHTML = '<i class="bi bi-check-circle-fill"></i> Reset!';
                    button.classList.remove('btn-outline-secondary');
                    button.classList.add('btn-success');
                    
                    setTimeout(() => {
                        button.innerHTML = originalText;
                        button.classList.remove('btn-success');
                        button.classList.add('btn-outline-secondary');
                    }, 2000);
                    
                    console.log('Colors reset to defaults');
                } catch (error) {
                    console.error('Error resetting colors:', error);
                    alert('Feil ved tilbakestilling av farger. Sjekk konsollen for detaljer.');
                }
            }
        });
    }

    // Initialize the color system
    console.log('Initializing color adjustment system...');
    initializeColorInputs();
    applyColorsToTable();
    console.log('Color adjustment system initialized');
});

// Adds color to the shift table
document.addEventListener('DOMContentLoaded', function() {
    // This function is now handled by the color adjustment system above
    // Keeping it for backward compatibility but it won't run if colors are already applied
    if (localStorage.getItem('shiftColorSettings')) {
        return; // Colors already applied by the new system
    }

    const tds = document.querySelectorAll('td[id="cell"]');
    tds.forEach(td => {
        const timeTextElement = td.querySelector('.time-text');
        if (timeTextElement) {
            // Clean up the timeText by removing newline characters and extra spaces
            let timeText = timeTextElement.textContent.trim();
            timeText = timeText.replace(/\s+/g, ' '); // Replace multiple spaces with a single space

            const times = timeText.split(' - ').map(time => time.trim());
            const customTextElement = td.querySelector('.custom-text');

            // Check if custom text ends with 'H' and add 'yellow' class
            if (customTextElement && customTextElement.textContent.trim().endsWith('H')) {
                td.classList.add('h-dag');
                return;
            }

            if (times.length > 1) {
                const startTime = times[0];
                const [start_hours, start_minutes] = startTime.split(':').map(Number);
                const startTotalMinutes = start_hours * 60 + start_minutes;

                const endTime = times[1];
                const [end_hours, end_minutes] = endTime.split(':').map(Number);
                const endTotalMinutes = end_hours * 60 + end_minutes;

                const late_shift = 16 * 60; // 16:01 in minutes
                const night_shift = 19 * 60;

                if (endTotalMinutes <= late_shift) {
                    td.classList.add('early');
                }
                if (endTotalMinutes > late_shift) {
                    td.classList.add('late');
                }
                if (startTotalMinutes >= night_shift) {
                    td.classList.add('night');
                }
                if (startTotalMinutes > endTotalMinutes) {
                    td.classList.add('late');
                }

                
                if (start_hours > 5 && start_hours < 9 && end_hours >= 16 && end_hours < 18){
                    td.classList.add('early-and-late')
                }

            } else {
                const listOfDaysoff = ['XX', 'OO', 'TT', ''];
                if (listOfDaysoff.includes(times[0])) {
                    td.classList.add('day_off');
                }
            }
        } else {
            console.log('No .time-text element found in td:', td); // Debugging statement
        }
    });
});

// Makes the submit button not clickable while submitting
function disableSubmitButton(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = true;
        submitButton.innerText = 'Submitting...';
    }
    return true;  // Ensure the form is submitted
}


// Funksjon for å lagre og hente opp hvor lang brukeren har scrollet på siden
const indexRoute = '/'
const specificRoute = window.location.pathname; // Define specificRoute based on the current path

// Save the scroll position before the user navigates away
if (window.location.pathname === indexRoute){
    window.addEventListener('beforeunload', function () {
        localStorage.setItem('scrollPosition', window.scrollY);
    }); 

    // Restore the scroll position after the page has fully loaded
    window.onload = function () {
        setTimeout(function () {
            const savedPosition = localStorage.getItem('scrollPosition-' + specificRoute);
            if (savedPosition) {
                window.scrollTo(0, parseInt(savedPosition));
            }
        }, 100);  // Delay restoration slightly to ensure content has loaded
    };

}


// TOGGLE FAVORITT
document.addEventListener('DOMContentLoaded', function() {
    // Use event delegation to handle change events on elements with the class 'toggle-favoritt'
    document.body.addEventListener('change', function(event) {
        if (event.target.classList.contains('toggle-favoritt')) {
            const isChecked = event.target.checked;
            const shiftTitle = event.target.getAttribute('shift_title');
            
            console.log('isChecked: ', isChecked, ',', 'ShiftTitle: ', shiftTitle)


            fetch('/api/toggle_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ favorite: isChecked, shift_title: shiftTitle })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });

    // Handle remove favorite button clicks (X buttons)
    document.body.addEventListener('click', function(event) {
        if (event.target.classList.contains('remove-favorite-btn')) {
            const shiftTitle = event.target.getAttribute('data-shift-title');
            
            console.log('Removing favorite:', shiftTitle);

            fetch('/api/toggle_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ favorite: false, shift_title: shiftTitle })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                // Remove the favorite item from the page after successful removal
                if (data.status === 'success') {
                    const favoriteItem = event.target.closest('.list-group-item');
                    if (favoriteItem) {
                        favoriteItem.remove();
                    }
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    });
});

// document.querySelector('form').addEventListener('submit', function(event) {
//     console.log('Form submitted');
// });


function printTables() {
    var printContents = '';
    var tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        var number =  table.closest('li').querySelector('.t-num').innerText;
        var name = table.closest('li').querySelector('.t-name').innerText;
        printContents += '<div class="print-frame"><h5>' + number +' - '+ name + '</h5>' + table.outerHTML + '</div><br>';
    });

    var originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}


function printAllTables() {
    var printContents = '';
    var tables = document.querySelectorAll('table');
    
    tables.forEach(function(table) {
        var name = table.closest('li').querySelector('.t-name').innerText;
        var dataFelt = table.closest('li').querySelector('.data-felt').outerHTML;
        
        printContents += '<div class="print-frame"><h4>' + name + '</h4>' + table.outerHTML + dataFelt + '</div><br>';
    });

    var originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}

// Turnusliste sorting functionality
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the turnusliste page
    const sortingContainer = document.querySelector('#helgetimer-slider');
    if (!sortingContainer) return;

    // Store original order of turnuser
    let originalOrder = [];
    let currentOrder = [];
    
    // Initialize original order
    function initializeOriginalOrder() {
        const turnusItems = document.querySelectorAll('.list-group-item');
        originalOrder = Array.from(turnusItems).map(item => {
            const turnusName = item.querySelector('.t-name').textContent.trim();
            return { element: item, name: turnusName };
        });
        currentOrder = [...originalOrder];
    }

    // Get turnus data from the page
    function getTurnusData() {
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

    // Calculate sorting score for a turnus
    function calculateScore(turnus, weights) {
        let score = 0;
        
        score += turnus.helgetimer * weights.helgetimer;
        score += turnus.shift_cnt * weights.shift_cnt;
        score += turnus.tidlig * weights.tidlig;
        score += turnus.natt * weights.natt;
        score += turnus.ettermiddag * weights.ettermiddag;
        score += turnus.before_6 * weights.before_6;
        score += turnus.afternoon_ends_before_20 * weights.afternoon_ends;
        
        return score;
    }

    // Sort turnuser based on current weights
    function sortTurnuser() {
        const weights = {
            helgetimer: parseFloat(document.getElementById('helgetimer-slider').value),
            shift_cnt: parseFloat(document.getElementById('shift-cnt-slider').value),
            tidlig: parseFloat(document.getElementById('tidlig-slider').value),
            natt: parseFloat(document.getElementById('natt-slider').value),
            ettermiddag: parseFloat(document.getElementById('ettermiddag-slider').value),
            before_6: parseFloat(document.getElementById('before-6-slider').value),
            afternoon_ends: parseFloat(document.getElementById('afternoon-ends-slider').value)
        };
        
        const turnusData = getTurnusData();
        
        if (turnusData.length === 0) {
            console.warn('No turnus data found');
            return;
        }
        
        // Calculate scores and sort
        turnusData.forEach(turnus => {
            turnus.score = calculateScore(turnus, weights);
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
        currentOrder = turnusData.map(t => ({ element: t.element, name: t.name }));
        
        // Update sorting info display
        updateSortingInfo(weights);
    }

    // Reset to original order
    function resetOrder() {
        const container = document.querySelector('.list-group');
        originalOrder.forEach(turnus => {
            container.appendChild(turnus.element);
        });
        currentOrder = [...originalOrder];
        
        // Reset all sliders
        const sliders = document.querySelectorAll('input[type="range"]');
        sliders.forEach(slider => {
            slider.value = 0;
            updateSliderValue(slider);
        });
    }

    // Update slider value display
    function updateSliderValue(slider) {
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
    }

    // Update sorting info display
    function updateSortingInfo(weights) {
        const sortingInfo = document.getElementById('sorting-info');
        const sortingCriteria = document.getElementById('sorting-criteria');
        
        if (!sortingInfo || !sortingCriteria) return;
        
        const activeCriteria = [];
        Object.entries(weights).forEach(([key, value]) => {
            if (value !== 0) {
                const label = getCriteriaLabel(key);
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

    // Get human-readable labels for criteria
    function getCriteriaLabel(key) {
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

    // Hide sorting info
    window.hideSortingInfo = function() {
        const sortingInfo = document.getElementById('sorting-info');
        if (sortingInfo) {
            sortingInfo.style.display = 'none';
        }
    };

    // Initialize
    initializeOriginalOrder();
    
    // Add event listeners to sliders
    const sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(slider => {
        slider.addEventListener('input', function() {
            updateSliderValue(this);
            sortTurnuser();
        });
    });
    
    // Add event listener to reset button
    const resetButton = document.getElementById('reset-sorting');
    if (resetButton) {
        resetButton.addEventListener('click', resetOrder);
    }
    
    // Initialize slider values
    sliders.forEach(updateSliderValue);
});