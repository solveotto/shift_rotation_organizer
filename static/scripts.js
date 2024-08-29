
// Makes shifts in the index-page clickable
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

            fetch('/api/receive-data', {
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
        const times = td.innerText.split(' - ');
        
        if (times.length > 1) {
            const startTime = times[0].trim();
            const [start_hours, start_minutes] = startTime.split(':').map(Number);
            const startTotalMinutes = start_hours * 60 + start_minutes;
            
            const endTime = times[1].trim();
            const [end_hours, end_minutes] = endTime.split(':').map(Number);
            const endTotalMinutes = end_hours * 60 + end_minutes;
            
            const late_shift = 16 * 60; // 16:00 in minutes
            const night_shift = 19 * 60;
            
            if (endTotalMinutes <= late_shift) {
                td.classList.add('early')
            }
            if (endTotalMinutes >= late_shift) {
                td.classList.add('late');
            }
            if (startTotalMinutes > late_shift && endTotalMinutes < startTotalMinutes) {
                td.classList.add('late');
            }
            if (startTotalMinutes < late_shift && endTotalMinutes < startTotalMinutes) {
                td.classList.add('late')
            }

            if (startTotalMinutes >= night_shift) {
                td.classList.add('night')
            }
        } else {
            const listOfDaysoff = ['XX', 'OO', 'TT']
            td.classList.add('day_off')
            if (listOfDaysoff.includes(times[0])) {
                td.classList.add('day_off')
            }
        }

    });
});


// Makes the submit button not clickable while submitting
function disableSubmitButton(form) {
    form.querySelector('button[type="submit"]').disabled = true;
    return true; }


// // When i input in the form is changed, it submits
// document.addEventListener('DOMContentLoaded', (event) => {
//     const form = document.getElementById('auto-submit-form');
//     const inputs = form.querySelectorAll('select');

//     inputs.forEach(input => {
//         input.addEventListener('change', () => {
//             form.submit();
//         });
//     });
// });