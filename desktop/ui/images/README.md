# Images Directory

This directory contains icon and image resources for the application UI.

## Required Images

### Button Icons (32x32 pixels recommended, PNG format with transparency)

1. **settings.png** - Settings/Configuration icon
   - Used for: Settings button in top-right corner
   - Style: Gear/cog icon, modern and clean design
   - Colors: Should work on both light and dark backgrounds

2. **theme.png** - Theme toggle icon
   - Used for: Theme switching button (light/dark mode)
   - Style: Sun/moon icon or lightbulb icon
   - Colors: Should indicate current theme state

3. **clear.png** - Clear/Clean icon
   - Used for: Clear chat button
   - Style: Trash can or X icon
   - Colors: Red or neutral gray

4. **history.png** - History icon
   - Used for: History button
   - Style: Clock, list, or document icon
   - Colors: Blue or neutral

5. **actions.png** - Actions/Menu icon
   - Used for: Unified actions button with dropdown menu
   - Style: Three dots (hamburger menu) or gear icon
   - Colors: Blue or neutral

6. **monitor.png** - Monitoring icon
   - Used for: Resource monitoring button
   - Style: Chart, graph, or dashboard icon
   - Colors: Green or blue

7. **backup.png** - Backup icon
   - Used for: Backup button
   - Style: Cloud, disk, or save icon
   - Colors: Blue or green

8. **quick_actions.png** - Quick actions icon
   - Used for: Quick actions button
   - Style: Lightning bolt or star icon
   - Colors: Yellow or orange

### Image Specifications

- **Format**: PNG with transparency (alpha channel)
- **Size**: 32x32 pixels (or 24x24 for smaller buttons)
- **Color Mode**: RGB with alpha channel
- **Background**: Transparent
- **Style**: Modern, flat design, consistent with Material Design or similar
- **Color Scheme**: Should work on both light (#FFFFFF) and dark (#2D2D2D) backgrounds

### Alternative: SVG Format

If using SVG format instead of PNG:
- **Format**: SVG
- **Size**: Scalable (vector)
- **Colors**: Use currentColor for theme compatibility
- **Files**: Same names but with .svg extension

## Usage in Code

Images should be loaded using:
```python
from PyQt5.QtGui import QIcon
icon = QIcon('desktop/ui/images/settings.png')
button.setIcon(icon)
```

## Notes

- All icons should have a consistent visual style
- Icons should be recognizable at small sizes (24-32px)
- Consider providing both light and dark variants if needed
- Ensure icons are optimized for file size while maintaining quality

