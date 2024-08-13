
// Dette scriptet gjør turnusene klikkbare
document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelectorAll('.clickable-row').forEach(row => {
        row.addEventListener('click', () => {
            const turnus = row.getAttribute('data-turnus');
            fetch('/api/receive-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ turnus: turnus })
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
});


document.addEventListener('DOMContentLoaded', function() {
    const tds = document.querySelectorAll('td[id="cell"]');
    tds.forEach(td => {
        const times = td.innerText.split(' - ');
        const firstTime = times[0].trim();
        const [hours, minutes] = firstTime.split(':').map(Number);
        const startTotalMinutes = hours * 60 + minutes;
        
        const late_shift = 16 * 60 + 30; // 16:00 in minutes
        const night_shift = 19 * 60;
        
        if (times.length > 1) {
            const endTime = times[1].trim();
            const [hours, minutes] = endTime.split(':').map(Number);
            const endTotalMinutes = hours * 60 + minutes;
            

            if (endTotalMinutes < late_shift) {
                td.classList.add('early')
            }
            if (endTotalMinutes >= late_shift) {
                td.classList.add('late');
            }
            if (startTotalMinutes > late_shift && endTotalMinutes < startTotalMinutes) {
                td.classList.add('late');
            }
            if (startTotalMinutes >= night_shift) {
                td.classList.add('night')
            }
        } else {
            const listOfDaysoff = ['XX', 'OO', 'TT']
            td.classList.add('day_off')
            if (listOfDaysoff.includes(firstTime)) {
                td.classList.add('day_off')
            }
        }

    });
});