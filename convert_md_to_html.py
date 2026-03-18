#!/usr/bin/env python3
"""
Markdown to HTML Converter with Enhanced Styling for Educational Materials
Converts markdown files to well-designed HTML with proper math rendering
"""

import re
import os
import sys
from pathlib import Path

def create_html_template():
    """Create a beautiful HTML template optimized for learning materials"""
    return """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- MathJax for proper math rendering -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
    </script>
    
    <style>
        :root {{
            --primary-color: #2c3e50;
            --secondary-color: #3498db;
            --accent-color: #e74c3c;
            --bg-color: #ffffff;
            --text-color: #2c3e50;
            --code-bg: #f8f9fa;
            --border-color: #e1e5e9;
            --shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Hiragino Sans', 'Meiryo', 'Yu Gothic', 'MS Gothic', sans-serif;
            line-height: 1.8;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }}
        
        h1 {{
            color: var(--primary-color);
            font-size: 2.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
            border-bottom: 3px solid var(--secondary-color);
            padding-bottom: 1rem;
        }}
        
        h2 {{
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-top: 2.5rem;
            margin-bottom: 1rem;
            border-left: 4px solid var(--secondary-color);
            padding-left: 1rem;
        }}
        
        h3 {{
            color: var(--primary-color);
            font-size: 1.4rem;
            margin-top: 2rem;
            margin-bottom: 0.8rem;
        }}
        
        h4 {{
            color: var(--secondary-color);
            font-size: 1.2rem;
            margin-top: 1.5rem;
            margin-bottom: 0.6rem;
        }}
        
        p {{
            margin-bottom: 1.2rem;
            text-align: justify;
        }}
        
        ul, ol {{
            margin-bottom: 1.2rem;
            padding-left: 2rem;
        }}
        
        li {{
            margin-bottom: 0.5rem;
        }}
        
        code {{
            background-color: var(--code-bg);
            padding: 0.2rem 0.4rem;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: var(--code-bg);
            padding: 1.5rem;
            border-radius: 8px;
            overflow-x: auto;
            margin: 1.5rem 0;
            box-shadow: var(--shadow);
        }}
        
        pre code {{
            background: none;
            padding: 0;
        }}
        
        blockquote {{
            border-left: 4px solid var(--secondary-color);
            margin: 1.5rem 0;
            padding: 1rem 1.5rem;
            background-color: #f8f9fa;
            font-style: italic;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: var(--shadow);
        }}
        
        th, td {{
            border: 1px solid var(--border-color);
            padding: 0.8rem;
            text-align: left;
        }}
        
        th {{
            background-color: var(--primary-color);
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        .math-block {{
            text-align: center;
            margin: 1.5rem 0;
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid var(--accent-color);
        }}
        
        .highlight-box {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        .note-box {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        .warning-box {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 1.5rem 0;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: var(--shadow);
            margin: 1rem 0;
        }}
        
        .toc {{
            background-color: #f8f9fa;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 1.5rem;
            margin: 2rem 0;
        }}
        
        .toc h2 {{
            margin-top: 0;
            color: var(--primary-color);
        }}
        
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        
        .toc li {{
            margin-bottom: 0.5rem;
        }}
        
        .toc a {{
            color: var(--secondary-color);
            text-decoration: none;
        }}
        
        .toc a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px 15px;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            h2 {{
                font-size: 1.5rem;
            }}
            
            pre {{
                padding: 1rem;
            }}
            
            table {{
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
{content}
    </div>
</body>
</html>"""

def convert_markdown_to_html(md_content):
    """Convert markdown content to HTML with enhanced formatting"""
    html = md_content
    
    # Convert headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    
    # Convert bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    
    # Convert code blocks
    html = re.sub(r'```(\w+)?\n(.*?)\n```', r'<pre><code>\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)
    
    # Convert blockquotes
    html = re.sub(r'^> (.+)$', r'<blockquote><p>\1</p></blockquote>', html, flags=re.MULTILINE)
    
    # Convert math expressions (preserve for MathJax)
    # Block math
    html = re.sub(r'\$\$([^$]+)\$\$', r'<div class="math-block">$$\1$$</div>', html)
    # Inline math - keep as is for MathJax
    
    # Convert lists
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Convert paragraphs
    paragraphs = html.split('\n\n')
    formatted_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p and not p.startswith('<'):
            p = f'<p>{p}</p>'
        formatted_paragraphs.append(p)
    
    html = '\n\n'.join(formatted_paragraphs)
    
    return html

def process_markdown_file(input_path, output_dir):
    """Process a single markdown file"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Get filename without extension
    filename = Path(input_path).stem
    title = filename.replace('_', ' ').title()
    
    # Convert to HTML
    html_content = convert_markdown_to_html(content)
    template = create_html_template()
    final_html = template.format(title=title, content=html_content)
    
    # Create output files
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Write HTML file
    html_output = output_dir / f"{filename}.html"
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    # Create improved markdown (with better formatting)
    improved_md = improve_markdown_formatting(content, title)
    md_output = output_dir / f"{filename}_improved.md"
    with open(md_output, 'w', encoding='utf-8') as f:
        f.write(improved_md)
    
    return html_output, md_output

def improve_markdown_formatting(content, title):
    """Improve markdown formatting while preserving content"""
    lines = content.split('\n')
    improved_lines = []
    
    improved_lines.append(f"# {title}")
    improved_lines.append("")
    improved_lines.append("---")
    improved_lines.append("")
    
    for line in lines:
        # Add spacing around headers
        if line.startswith('#'):
            if improved_lines and improved_lines[-1] != "":
                improved_lines.append("")
            improved_lines.append(line)
            improved_lines.append("")
        # Add spacing around code blocks
        elif line.startswith('```'):
            improved_lines.append("")
            improved_lines.append(line)
        # Add spacing after paragraphs
        elif line.strip() == "" and improved_lines and improved_lines[-1] != "":
            improved_lines.append(line)
        else:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)

if __name__ == "__main__":
    # Example usage
    input_files = [
        "md_boost_design_final.md",
        "md_control_theory_final.md"
    ]
    
    output_directory = "converted_documents"
    
    for file_path in input_files:
        if os.path.exists(file_path):
            print(f"Processing {file_path}...")
            html_output, md_output = process_markdown_file(file_path, output_directory)
            print(f"Created: {html_output}")
            print(f"Created: {md_output}")
        else:
            print(f"File not found: {file_path}")