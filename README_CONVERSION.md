# Markdown to HTML Converter for Learning Materials

This repository contains a comprehensive system for converting markdown files into beautifully styled HTML and improved markdown formats, specifically designed for educational content.

## Features

### 🎨 Beautiful HTML Output
- **Professional Design**: Clean, modern layout optimized for learning
- **Math Formula Support**: MathJax integration for perfect LaTeX math rendering
- **Japanese Typography**: Optimized fonts (Hiragino Sans, Meiryo, Yu Gothic)
- **Responsive Design**: Mobile-friendly layout
- **Accessibility**: High contrast colors and proper spacing

### 📚 Enhanced Styling
- **Visual Hierarchy**: Color-coded headers and sections
- **Math Highlighting**: Special styling for mathematical formulas
- **Code Blocks**: Syntax highlighting and proper formatting
- **Professional Tables**: Clean borders and alternating row colors
- **Interactive Elements**: Hover effects and shadows

### 🔧 Technical Features
- **UTF-8 Support**: Proper handling of Japanese and mathematical characters
- **Cross-browser Compatibility**: Works on all modern browsers
- **Print-friendly**: Optimized CSS for printing
- **No External Dependencies**: Self-contained HTML files

## Usage

### Method 1: Using the Python Script

```bash
python3 convert_md_to_html.py
```

The script will look for these files:
- `md_boost_design_final.md`
- `md_control_theory_final.md`

And create:
- `converted_documents/md_boost_design_final.html`
- `converted_documents/md_control_theory_final.html`
- `converted_documents/md_boost_design_final_improved.md`
- `converted_documents/md_control_theory_final_improved.md`

### Method 2: Manual Conversion

1. Copy your markdown content
2. Use the HTML template in `convert_md_to_html.py`
3. Replace `{title}` and `{content}` placeholders
4. Save as `.html` file

## File Structure

```
├── convert_md_to_html.py          # Main conversion script
├── sample_boost_design.html        # Example HTML output
├── sample_control_theory.html      # Example HTML output
├── sample_boost_design_improved.md # Example improved markdown
├── sample_control_theory_improved.md # Example improved markdown
└── README_CONVERSION.md            # This file
```

## Sample Output

The system creates beautiful educational materials with:

- **Clear Typography**: Easy-to-read fonts and proper spacing
- **Mathematical Formulas**: Properly rendered with MathJax
- **Color-coded Sections**: Visual organization for better learning
- **Mobile Responsive**: Readable on all devices

## Mathematical Formula Support

The system supports both inline and block mathematics:

- Inline math: `$V_{out} = \frac{V_{in}}{1-D}$`
- Block math: `$$G(s) = \frac{Y(s)}{U(s)}$$`

## Customization

You can modify the CSS in the HTML template to:
- Change color scheme
- Adjust typography
- Modify spacing and layout
- Add custom styling for specific elements

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Notes

- The conversion preserves all original content
- Mathematical formulas are enhanced for better visibility
- Tables and lists are styled for improved readability
- Code blocks maintain proper formatting