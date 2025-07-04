# F1 Dashboard CSS Structure

This directory contains the stylesheets for the F1 Dashboard application.

## File Structure

- **style.css**: Main application stylesheet used across the dashboard and authenticated pages
- **home.css**: Specialized stylesheet for the marketing home/landing page only
- **animations.css**: Contains animation-specific CSS rules that can be used across the application

## Style Guidelines

When adding new styles to the project, follow these guidelines:

1. Place page-specific styles in their appropriate files
2. Use CSS variables defined in `:root` for consistent theming
3. Follow the existing naming conventions for classes
4. Add meaningful comments for complex styling logic
5. Organize new styles according to the sections in the table of contents

## CSS Variables

The main color scheme and variables are defined at the top of each stylesheet:

```css
:root {
    --f1-red: #e10600;
    --f1-dark-red: #a50000;
    --f1-black: #121212;
    --f1-dark-gray: #222222;
    --f1-light-gray: #f1f1f1;
    /* other variables */
}
```

## Media Queries

Media queries for responsive design are located at the bottom of each stylesheet. When adding new responsive styles, add them to the appropriate media query blocks based on screen size.

## Animation Effects

The project uses several custom animations for UI elements. Most animations are defined in the `animations.css` file, but component-specific animations may be defined in their respective stylesheets.

## Maintenance

If making significant changes to the CSS structure, please update this README accordingly. 