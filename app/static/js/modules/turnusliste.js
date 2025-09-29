// Highlight Navigation Module
// Handles highlighting and auto-scrolling to specific turnus items

// Global function for handling key button clicks
function handleKeyFunction(turnusName) {
    console.log('handleKeyFunction called with turnusName:', turnusName);
    
    // Get the current turnus set ID from the page
    const turnusSetId = getCurrentTurnusSetId();
    console.log('Retrieved turnusSetId:', turnusSetId);
    
    if (!turnusSetId) {
        console.log('No turnus set ID found, showing error');
        alert('Kunne ikke finne aktiv turnus-sett');
        return;
    }
    
    // Show loading state (optional)
    console.log(`Generating turnusnøkkel for: ${turnusName}`);
    
    // Call the API
    fetch('/api/generate-turnusnokkel', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            turnus_name: turnusName,
            turnus_set_id: turnusSetId
        })
    })
    .then(response => {
        if (response.ok) {
            // Get the filename from the Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `Turnusnøkkel_${turnusName}.xlsx`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
                if (filenameMatch && filenameMatch[1]) {
                    filename = filenameMatch[1].replace(/['"]/g, '');
                }
            }
            
            // Create a blob and trigger download
            return response.blob().then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                console.log(`Downloaded: ${filename}`);
            });
        } else {
            // Handle error response
            return response.json().then(data => {
                throw new Error(data.message || 'Unknown error occurred');
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert(`Feil ved generering: ${error.message}`);
    });
}

// Helper function to get current turnus set ID
function getCurrentTurnusSetId() {
    // Try to get from the printable container
    const printableContainer = document.querySelector('.printable');
    if (printableContainer && printableContainer.dataset.currentTurnusSetId) {
        const idValue = printableContainer.dataset.currentTurnusSetId;
        if (idValue === 'null' || idValue === null || idValue === '') {
            console.log('Turnus set ID is null or empty');
            return null;
        }
        const id = parseInt(idValue);
        console.log('Found turnus set ID from printable container:', id);
        return id;
    }
    
    // Try to get from hidden input
    const hiddenInput = document.querySelector('input[name="current_turnus_set_id"]');
    if (hiddenInput) {
        const id = parseInt(hiddenInput.value);
        console.log('Found turnus set ID from hidden input:', id);
        return id;
    }
    
    // Try to get from data attribute on body
    const body = document.body;
    if (body.dataset.currentTurnusSetId) {
        const id = parseInt(body.dataset.currentTurnusSetId);
        console.log('Found turnus set ID from body:', id);
        return id;
    }
    
    // Fallback: look for turnus set info in the page
    const turnusSetInfo = document.querySelector('[data-turnus-set-id]');
    if (turnusSetInfo) {
        const id = parseInt(turnusSetInfo.dataset.turnusSetId);
        console.log('Found turnus set ID from generic selector:', id);
        return id;
    }
    
    console.log('No turnus set ID found');
    return null;
}

document.addEventListener('DOMContentLoaded', function() {
    const highlightedElement = document.querySelector('.highlighted-turnus');
    
    if (highlightedElement) {
        // Jump to highlighted element
        setTimeout(() => {
            const rect = highlightedElement.getBoundingClientRect();
            const elementTop = rect.top + window.pageYOffset;
            const elementHeight = rect.height;
            const windowHeight = window.innerHeight;
            const scrollTo = elementTop - (windowHeight / 2) + (elementHeight / 2);
            
            window.scrollTo(0, scrollTo);
        }, 1000);
        
        // Remove highlight when clicking anywhere else
        document.addEventListener('click', function(event) {
            if (!highlightedElement.contains(event.target)) {
                highlightedElement.classList.remove('highlighted-turnus');
                const url = new URL(window.location);
                url.searchParams.delete('turnus');
                window.history.replaceState({}, '', url);
            }
        });
    }
});