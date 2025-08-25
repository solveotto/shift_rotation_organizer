# Color Adjustment Feature for Shift Tables

## Overview
The shift rotation organizer now includes a color adjustment system that allows users to customize the colors and time thresholds for different types of shifts in the `turnusliste.html` page.

## Features

### Color Customization
Users can adjust colors for the following shift types:
- **Tidlig skift (Early shift)**: Default color: Aqua (#00ffff)
- **Kveldsskift (Evening shift)**: Default color: Light red (#ff9696)
- **Nattskift (Night shift)**: Default color: Magenta (#eb41eb)
- **Fridager (Days off)**: Default color: Green (#42bb42)
- **H-dager (H-days)**: Default color: Gold (#ffd700)
- **Tidlig + Kveld (Early + Evening)**: Default color: Blue (#268eb8)

### Time Threshold Adjustment
Users can modify the time thresholds that determine when certain colors apply:
- **Early shift threshold**: When a shift ends before this time (default: 16:00)
- **Late shift threshold**: When a shift ends after this time (default: 16:00)
- **Night shift threshold**: When a shift starts after this time (default: 19:00)

### Persistent Settings
- All color and time settings are automatically saved to the browser's localStorage
- Settings persist between browser sessions
- Users can reset to default values at any time

## How to Use

### Accessing the Color Panel
1. Navigate to the `turnusliste.html` page
2. Look for the left sidebar with the "Fargeinnstillinger" (Color Settings) section
3. The color panel appears above the sorting controls

### Changing Colors
1. Click on any color input to open the color picker
2. Select your desired color
3. Click "Bruk farger" (Use Colors) to apply the changes

### Adjusting Time Thresholds
1. Modify the time inputs for early, late, and night shifts
2. Use the format HH:MM (24-hour format)
3. Click "Bruk farger" to apply the changes

### Resetting to Defaults
1. Click "Reset farger" (Reset Colors) button
2. Confirm the reset action
3. All colors and times will return to their default values

## Technical Implementation

### Files Modified
- `app/templates/turnusliste.html`: Added color adjustment panel to sidebar
- `app/static/scripts.js`: Implemented color adjustment logic and localStorage persistence
- `app/static/styles.css`: Added styling for the color panel and enhanced sidebar appearance

### JavaScript Functions
- `loadColorSettings()`: Loads saved settings from localStorage
- `saveColorSettings()`: Saves current settings to localStorage
- `applyColorsToTable()`: Applies colors to shift table cells based on current settings
- `initializeColorInputs()`: Sets up color inputs with current values

### CSS Classes Added
- `.color-input-group`: Styles for color input containers
- `.sidebar-header`: Enhanced sidebar section headers
- `.sidebar-content`: Improved sidebar content styling
- Enhanced responsive design for mobile devices

## Browser Compatibility
- Modern browsers with localStorage support
- Responsive design works on desktop, tablet, and mobile devices
- Color inputs use native HTML5 color pickers

## Troubleshooting

### Colors Not Applying
1. Check browser console for JavaScript errors
2. Ensure you're on the correct page (`turnusliste.html`)
3. Verify that the color panel is visible in the sidebar

### Settings Not Saving
1. Check if localStorage is enabled in your browser
2. Try refreshing the page after making changes
3. Check browser console for any error messages

### Performance Issues
1. The color system only runs on the turnusliste page
2. Colors are applied once when the page loads
3. Additional color applications only occur when manually triggered

## Future Enhancements
- Export/import color schemes
- Additional shift type categories
- Advanced color rules (e.g., weekend-specific colors)
- Integration with user preferences system
