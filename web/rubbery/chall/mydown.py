import logging
import os
import re
import subprocess
import tempfile
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter

logger = logging.getLogger(__name__)


def render_title(content: str, level: int) -> str:
    """Render title blocks with appropriate heading levels."""
    escaped_content = content.strip()
    return f"<h{level}>{escaped_content}</h{level}>"


def render_paragraph(content: str) -> str:
    """Render paragraph blocks, converting line breaks to <br> tags."""
    if not content.strip():
        return ""

    # Replace single newlines with <br> tags, but preserve paragraph breaks
    lines = content.strip().split('\n')
    processed_lines = []

    for line in lines:
        if line.strip():
            processed_lines.append(line.strip())

    # Join lines with <br> tags
    paragraph_content = '<br>\n'.join(processed_lines)
    return f"<p>{paragraph_content}</p>"


def render_code(content: str, language: str = None) -> str:
    html_data = '<span style="color:red">ERROR rendering code</span>'

    try:
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            with open(os.path.join(temp_dir, 'input.txt'), 'w') as f:
                f.write(content)

            subprocess.run([
                'pygmentize',
                '-l', language,
                '-f', 'html',
                '-o', 'output.html',
                'input.txt',
            ], cwd=temp_dir)

            with open(os.path.join(temp_dir, 'output.html'), 'rb') as f:
                html_data = f.read().decode()
    except:
        pass

    return html_data


def render_math(content: str) -> str:
    svg_data = '<span style="color:red">ERROR rendering math</span>'

    try:
        with tempfile.TemporaryDirectory(delete=False) as temp_dir:
            print("Temp path:", temp_dir)
            with open(os.path.join(temp_dir, 'math.tex'), 'w') as f:
                f.write(r"""
\documentclass[preview]{standalone}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}

\thispagestyle{empty}
\begin{document}
$$""" + content + r"""$$
\end{document}
""")

            res1 = subprocess.run(['tectonic', '-X', 'compile', '--untrusted', 'math.tex'], cwd=temp_dir)
            assert res1.returncode == 0, "tectonic command failed"
            res2 = subprocess.run(['pdf2svg', 'math.pdf', 'math.svg'], cwd=temp_dir)
            assert res2.returncode == 0, "pdf2svg command failed"

            with open(os.path.join(temp_dir, 'math.svg'), 'rb') as f:
                svg_data = f.read().decode()
    except:
        logger.exception("Error rendering math")


    return f'<div class="math-display">{svg_data}</div>'


def render_mydown(mydown_code: str) -> str:
    """
    Main function to render MyDown markup to HTML.

    Block types:
    - | = h1 title
    - || = h2 subtitle
    - ||| = h3 subtitle
    - /code:language ... code/ = code block
    - /math ... math/ = math block
    - Regular text = paragraphs
    """
    if not mydown_code.strip():
        return ""

    lines = mydown_code.split('\n')
    html_blocks = []
    current_block = []
    current_block_type = 'paragraph'
    in_code_block = False
    in_math_block = False
    code_language = None

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check for code block start
        code_start_match = re.match(r'^/code(?::(\w+))?$', line.strip())
        if code_start_match and not in_math_block:
            # Finish current paragraph block if any
            if current_block and current_block_type == 'paragraph':
                content = '\n'.join(current_block)
                if content.strip():
                    html_blocks.append(render_paragraph(content))
                current_block = []

            in_code_block = True
            code_language = code_start_match.group(1)
            current_block_type = 'code'
            current_block = []
            i += 1
            continue

        # Check for code block end
        if line.strip() == 'code/' and in_code_block:
            content = '\n'.join(current_block)
            html_blocks.append(render_code(content, code_language))
            in_code_block = False
            code_language = None
            current_block = []
            current_block_type = 'paragraph'
            i += 1
            continue

        # Check for math block start
        if line.strip() == '/math' and not in_code_block:
            # Finish current paragraph block if any
            if current_block and current_block_type == 'paragraph':
                content = '\n'.join(current_block)
                if content.strip():
                    html_blocks.append(render_paragraph(content))
                current_block = []

            in_math_block = True
            current_block_type = 'math'
            current_block = []
            i += 1
            continue

        # Check for math block end
        if line.strip() == 'math/' and in_math_block:
            content = '\n'.join(current_block)
            html_blocks.append(render_math(content))
            in_math_block = False
            current_block = []
            current_block_type = 'paragraph'
            i += 1
            continue

        # If we're in a code or math block, just collect lines
        if in_code_block or in_math_block:
            current_block.append(line)
            i += 1
            continue

        # Check for titles (must not be in code/math blocks)
        title_match = re.match(r'^(\|{1,3})\s+(.+)$', line)
        if title_match:
            # Finish current paragraph block if any
            if current_block and current_block_type == 'paragraph':
                content = '\n'.join(current_block)
                if content.strip():
                    html_blocks.append(render_paragraph(content))
                current_block = []

            # Render title
            level = len(title_match.group(1))
            title_content = title_match.group(2)
            html_blocks.append(render_title(title_content, level))
            current_block_type = 'paragraph'
            i += 1
            continue

        # Handle empty lines - they separate paragraphs
        if not line.strip():
            if current_block and current_block_type == 'paragraph':
                content = '\n'.join(current_block)
                if content.strip():
                    html_blocks.append(render_paragraph(content))
                current_block = []
            i += 1
            continue

        # Regular text line - add to current paragraph
        if current_block_type == 'paragraph':
            current_block.append(line)

        i += 1

    # Handle any remaining block
    if current_block:
        if current_block_type == 'paragraph':
            content = '\n'.join(current_block)
            if content.strip():
                html_blocks.append(render_paragraph(content))
        elif current_block_type == 'code':
            content = '\n'.join(current_block)
            html_blocks.append(render_code(content, code_language))
        elif current_block_type == 'math':
            content = '\n'.join(current_block)
            html_blocks.append(render_math(content))

    return '\n'.join(html_blocks)
