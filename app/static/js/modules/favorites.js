// Favorites Module
// Handles favorite toggle functionality

export class Favorites {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        console.log('Setting up favorites event listeners...');
        
        // Use event delegation to handle change events on elements with the class 'toggle-favoritt'
        document.body.addEventListener('change', (event) => {
            if (event.target.classList.contains('toggle-favoritt')) {
                this.handleToggleFavorite(event);
            }
        });

        // Handle remove favorite button clicks (X buttons)
        document.body.addEventListener('click', (event) => {
            if (event.target.classList.contains('remove-favorite-btn')) {
                console.log('Remove favorite button clicked!');
                this.handleRemoveFavorite(event);
            }
        });
        
        console.log('Favorites event listeners set up successfully');
    }

    handleToggleFavorite(event) {
        const isChecked = event.target.checked;
        const shiftTitle = event.target.getAttribute('shift_title');
        
        console.log('isChecked: ', isChecked, ',', 'ShiftTitle: ', shiftTitle);

        this.updateFavoriteStatus(isChecked, shiftTitle);
    }

    handleRemoveFavorite(event) {
        const shiftTitle = event.target.getAttribute('data-shift-title');
        
        console.log('Removing favorite:', shiftTitle);

        if (!shiftTitle) {
            console.error('No shift title found for remove button');
            return;
        }

        this.updateFavoriteStatus(false, shiftTitle)
            .then(data => {
                // Remove the favorite item from the page after successful removal
                if (data.status === 'success') {
                    const favoriteItem = event.target.closest('.list-group-item');
                    if (favoriteItem) {
                        favoriteItem.remove();
                        console.log('Favorite removed from page');
                    } else {
                        console.warn('Could not find favorite item to remove from page');
                    }
                } else {
                    console.error('Failed to remove favorite:', data.message);
                    alert('Feil ved fjerning av favoritt: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error removing favorite:', error);
                alert('Feil ved fjerning av favoritt');
            });
    }

    async updateFavoriteStatus(favorite, shiftTitle) {
        try {
            const response = await fetch('/api/toggle_favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ favorite: favorite, shift_title: shiftTitle })
            });

            const data = await response.json();
            console.log('Success:', data);
            return data;
        } catch (error) {
            console.error('Error:', error);
            throw error;
        }
    }
}
