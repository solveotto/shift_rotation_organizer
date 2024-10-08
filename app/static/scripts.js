
// Makes shifts checkbox in the index-page clickable
document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', () => {
            const turnus = row.getAttribute('data-turnus');
            const checkbox = row.querySelector('.prevent-click');
            const isChecked = checkbox ? checkbox.checked : false;

            if (isChecked) {
                console.log('Checkbox is checked:', isChecked);
                console.log('Turnus:', turnus);
            }

            fetch('/api/js_select_shift', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ turnus: turnus, checked: isChecked })
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

// Adds color to the shift table
document.addEventListener('DOMContentLoaded', function() {
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
                if (startTotalMinutes > late_shift && endTotalMinutes < startTotalMinutes) {
                    td.classList.add('late');
                }
                if (startTotalMinutes < late_shift && endTotalMinutes < startTotalMinutes) {
                    td.classList.add('late');
                }
                if (startTotalMinutes >= night_shift) {
                    td.classList.add('night');
                }

                
                if (startTotalMinutes > endTotalMinutes){
                    td.classList.add('late')
                }

                if (start_hours > 6 && start_hours < 9 && end_hours > 16 && end_hours < 18){
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


document.addEventListener('DOMContentLoaded', function () {
    var sortableList = document.getElementById('sortable-list');
    if (sortableList) {
        var sortable = Sortable.create(sortableList, {
            animation: 150,
            ghostClass: 'sortable-ghost',
    
            onEnd: function(/** */evt) {
                // Disable sorting until the response is received
                sortable.option("disabled", true);
                document.body.style.cursor = 'wait';
                // Oppdaterer rekkefølgen av listen når bruker endrer den
                var order = []
                var items = sortableList.querySelectorAll('.list-group-item');
                items.forEach(function (item) {
                    order.push(item.getAttribute('data-name').trim());
                });
                // Sender innholdet i listen til Flask server
                
                fetch('/update-order', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({order:order})
                
                }).then(response => {
                    if (response.ok) {
                        sortable.option("disabled", false);
                        console.log('Order updated successfully!');
                        window.location.reload();
                    } else {
                        console.error('Failed to update order.');
                        sortable.option("disabled", false);
                        document.body.style.cursor = 'default';
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    // Re-enable sorting if there is an error
                    sortable.option("disabled", false);
                    document.body.style.cursor = 'default';
                });
            }
        });
    }
});



// FOR Å DETEKTERE FAVORITT
document.addEventListener('DOMContentLoaded', function() {
    const inputElement = document.getElementById('id-of-input');
    if (inputElement) {
        inputElement.addEventListener('change', function() {
            const isChecked = this.checked;
            const shiftTitle = this.getAttribute('shift_title');
            
            fetch('/toggle_favorite', {
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
        });
    } 
});


document.querySelector('form').addEventListener('submit', function(event) {
    console.log('Form submitted');
});


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