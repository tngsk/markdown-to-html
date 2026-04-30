const hljs = require('highlight.js');
const fs = require('fs');

// Read JSON input from stdin
let inputData = '';
process.stdin.on('data', chunk => {
    inputData += chunk;
});

process.stdin.on('end', () => {
    try {
        const data = JSON.parse(inputData);
        const { code, language } = data;

        let highlightedCode = '';
        if (language && hljs.getLanguage(language)) {
            highlightedCode = hljs.highlight(code, { language }).value;
        } else {
            highlightedCode = hljs.highlightAuto(code).value;
        }

        console.log(highlightedCode);
    } catch (e) {
        console.error(e);
        process.exit(1);
    }
});
