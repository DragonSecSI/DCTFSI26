// Initialize Monaco Editor
require.config({ paths: { 'vs': 'https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs' }});
require(['vs/editor/editor.main'], function() {
  const $editor = document.getElementById('editor')
  const template = $editor.innerText
  $editor.innerHTML = ''
    const editor = monaco.editor.create($editor, {
        value: template,
        language: 'mydown',
        theme: 'vs-light',
        automaticLayout: true,
        wordWrap: 'on'
    });

    // Render mydown on load
    setTimeout(() => {
        rendermydown(editor.getValue());
    }, 500);

    // Handle render button click
    document.getElementById('render-btn').addEventListener('click', function() {
        const mydownText = editor.getValue();
        rendermydown(mydownText);
    });

    function rendermydown(mydownText) {
        // Create form data
        const formData = new FormData();
        formData.append('mydown_text', mydownText);

        // Send POST request to backend
        fetch('/render', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(html => {
            document.getElementById('rendered-content').innerHTML = html;
        })
        .catch(error => {
            console.error('Error rendering mydown:', error);
            document.getElementById('rendered-content').innerHTML = '<p>Error rendering mydown</p>';
        });
    }
});
