# JavaScript Module Structure

This directory contains the modular JavaScript architecture for the shift rotation organizer.

## Module Overview

### 1. `shift-selection.js` - ShiftSelection Class
- Handles clickable table rows
- Manages shift selection API calls
- Prevents checkbox click propagation

### 2. `shift-colors.js` - ShiftColors Class
- **CORE COLOR LOGIC** - Applies CSS classes to table cells
- Default shift color application (early, late, night, day_off, h-dag, early-and-late)
- Works with existing CSS color definitions
- Respects user custom color settings

### 3. `color-adjustment.js` - ColorAdjustment Class  
- **USER INTERFACE** for color customization 
- Manages localStorage for custom color settings
- Provides color picker and time threshold controls
- Applies custom colors via inline styles (overrides CSS classes)

### 4. `favorites.js` - Favorites Class
- Toggle favorite shifts functionality
- Remove favorites with X buttons
- API communication for favorite status

### 5. `sorting-system.js` - SortingSystem Class (To be created)
- Turnusliste sorting functionality
- Weight-based scoring system
- Settings persistence

### 6. `utils.js` - Utility Functions
- Form submission helpers
- Print functionality
- Scroll position management
- Shared utility functions

### 7. `main.js` - App Coordinator
- Module initialization and coordination
- Conditional loading based on page context
- Global app instance management

## How to Use

### In your HTML templates:

Replace the old script tag:
```html
<script src="{{ url_for('static', filename='scripts.js') }}" defer></script>
```

With the new modular approach:
```html
<script type="module" src="{{ url_for('static', filename='js/main.js') }}" defer></script>
```

### Page-specific modules:

You can also load specific modules for certain pages:

```html
<!-- For turnusliste page only -->
{% block extra_js %}
<script type="module">
    import { ColorAdjustment } from '{{ url_for("static", filename="js/modules/color-adjustment.js") }}';
    import { SortingSystem } from '{{ url_for("static", filename="js/modules/sorting-system.js") }}';
    
    // Initialize page-specific functionality
    new ColorAdjustment();
    new SortingSystem();
</script>
{% endblock %}
```

## Migration Steps

1. **Create the sorting-system.js module** (extract from current scripts.js lines 502-880)
2. **Update base.html** to use `main.js` instead of `scripts.js`
3. **Remove legacy code** from the old `scripts.js`
4. **Test each module** individually
5. **Add any missing functionality**

## Benefits

- **Modularity**: Each feature is self-contained
- **Performance**: Only load what you need
- **Maintainability**: Easier to debug and update
- **Reusability**: Modules can be used independently
- **Modern**: Uses ES6 modules and classes
- **Testability**: Each module can be tested in isolation

## Legacy Compatibility

The `utils.js` module maintains backward compatibility by exposing global functions:
- `window.printTables`
- `window.disableSubmitButton`

This ensures existing HTML onclick handlers continue to work during migration.
