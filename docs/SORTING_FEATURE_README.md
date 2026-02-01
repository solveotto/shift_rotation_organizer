# Turnusliste Sorting Feature

## Overview
The Turnusliste page now includes an interactive sorting system that allows users to dynamically reorder turnuser based on various criteria using sliders.

## Features

### Sorting Criteria
The system includes sliders for the following criteria:

1. **Helgetimer** - Weekend hours
2. **Dagsverk** - Number of work days
3. **Tidlig** - Early shifts
4. **Natt** - Night shifts
5. **Ettermiddag** - Afternoon shifts
6. **Før 6:00** - Shifts starting before 6:00 AM
7. **Slutt før 20:00** - Shifts ending before 8:00 PM

### How It Works

#### Slider Values
- **Range**: -10 to +10 (with 0.5 step increments)
- **Positive values**: Higher values move to the top (Høy → Lav)
- **Negative values**: Lower values move to the top (Lav → Høy)
- **Zero**: No effect on sorting

#### Real-time Sorting
- Sorting happens automatically as you move the sliders
- Multiple criteria can be combined for complex sorting
- The system calculates a weighted score for each turnus based on all active criteria

#### Visual Feedback
- **Green badges**: Positive slider values
- **Gray badges**: Zero or negative slider values
- **Sorting info alert**: Shows active sorting criteria
- **Reset button**: Returns to original order and resets all sliders

## Usage Examples

### Example 1: Prioritize Low Weekend Hours
- Move "Helgetimer" slider to the left (negative value)
- Turnuser with fewer weekend hours will appear at the top

### Example 2: Prioritize High Shift Count
- Move "Dagsverk" slider to the right (positive value)
- Turnuser with more work days will appear at the top

### Example 3: Complex Sorting
- Set "Helgetimer" to -5 (prioritize low weekend hours)
- Set "Dagsverk" to +3 (slightly prioritize high shift count)
- The system will balance both criteria

## Technical Implementation

### Files Modified
- `app/templates/turnusliste.html` - Added sorting controls and display
- `app/static/scripts.js` - Added sorting logic and event handlers
- `app/static/styles.css` - Added styling for sliders and controls

### JavaScript Functions
- `getTurnusData()` - Extracts turnus data from the DOM
- `calculateScore()` - Computes weighted scores for sorting
- `sortTurnuser()` - Performs the actual sorting and reordering
- `updateSortingInfo()` - Updates the sorting criteria display
- `resetOrder()` - Restores original order

### Data Extraction
The system automatically extracts the following data from each turnus:
- Shift count, early shifts, afternoon shifts, night shifts
- Weekend hours, shifts before 6:00 AM, shifts ending before 8:00 PM

## Browser Compatibility
- Modern browsers with ES6 support
- Responsive design for mobile and desktop
- Cross-browser slider styling (WebKit, Firefox, Edge)

## Future Enhancements
Potential improvements could include:
- Saving user preferences
- More sorting criteria
- Advanced filtering options
- Export sorted results
- Undo/redo functionality

## Troubleshooting
If sorting doesn't work:
1. Check browser console for JavaScript errors
2. Verify all turnuser have the required data fields
3. Ensure the page is fully loaded before using sliders
4. Try refreshing the page if issues persist
