/**
 * Code Block Enhancement
 * - Syntax highlighting with Highlight.js
 * - Copy-to-clipboard functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Highlight.js
    initializeSyntaxHighlighting();

    // Initialize copy buttons
    initializeCopyButtons();
});

/**
 * Initialize syntax highlighting for code blocks
 */
function initializeSyntaxHighlighting() {
    if (typeof hljs === 'undefined') {
        console.warn('Highlight.js not loaded');
        return;
    }

    document.querySelectorAll('.hljs').forEach(el => {
        hljs.highlightElement(el);
    });
}

/**
 * Initialize copy button functionality
 */
function initializeCopyButtons() {
    document.querySelectorAll('.copy-button').forEach(button => {
        button.addEventListener('click', handleCopyClick);
    });
}

/**
 * Handle copy button click event
 * @param {Event} event - Click event
 */
function handleCopyClick(event) {
    const button = event.currentTarget;
    const codeBlock = button.closest('.code-block-wrapper');

    if (!codeBlock) {
        console.error('Code block wrapper not found');
        return;
    }

    const codeElement = codeBlock.querySelector('code');
    if (!codeElement) {
        console.error('Code element not found');
        return;
    }

    const text = codeElement.textContent;

    navigator.clipboard.writeText(text)
        .then(() => {
            showCopySuccess(button);
        })
        .catch(err => {
            showCopyError(button);
            console.error('Copy failed:', err);
        });
}

/**
 * Show success state after copy
 * @param {HTMLElement} button - Copy button element
 */
function showCopySuccess(button) {
    const originalText = button.textContent;
    button.textContent = '✓ Copied!';
    button.classList.add('copied');

    setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('copied');
    }, 2000);
}

/**
 * Show error state after copy failure
 * @param {HTMLElement} button - Copy button element
 */
function showCopyError(button) {
    const originalText = button.textContent;
    button.textContent = '✗ Failed';

    setTimeout(() => {
        button.textContent = originalText;
    }, 2000);
}
