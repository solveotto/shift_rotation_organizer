// Highlight Navigation Module
// Handles highlighting and auto-scrolling to specific turnus items

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