import re

css = """
:host {
    display: flex;
    flex-direction: column;
    height: 100%;
    margin: 0;
    font-family: var(--mono-font-family, system-ui, -apple-system, sans-serif);
    color: var(--mono-text-color, var(--color-base-content));
    background: var(--mono-bg-color, var(--color-base-200));
    border: 1px solid var(--mono-border-color, var(--border-color));
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    max-width: 600px;
    box-sizing: border-box;
}

.poll-wrapper {
    display: flex;
    flex-direction: column;
    flex: 1;
    padding: 1.5rem;
    box-sizing: border-box;
}

.poll-header {
    margin-top: 0;
    margin-bottom: 1rem;
    font-size: 1.1rem;
    font-weight: 600;
    line-height: 1.4;
}

.options-container {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
}

.option-label {
    display: flex;
    align-items: center;
    padding: 0.75rem 1rem;
    border: 1px solid var(--mono-border-color, var(--border-color));
    border-radius: 6px;
    background: var(--color-base-100);
    cursor: pointer;
    transition: background-color 0.15s ease, border-color 0.15s ease;
}

.option-label:hover:not(.voted) {
    background: var(--mono-hover-bg, var(--color-base-200));
}

.option-label.selected {
    border-color: var(--mono-primary-color, var(--color-primary));
    background: var(--mono-primary-light, var(--color-primary-light));
}

input[type="radio"] {
    margin-right: 1rem;
    transform: scale(1.2);
    cursor: pointer;
}

.submit-container {
    margin-top: auto;
    display: flex;
    flex-direction: column;
}

button.submit-btn {
    margin-top: 1.5rem;
    padding: 0.5rem 1.5rem;
    background-color: var(--mono-primary-color, var(--color-primary));
    color: var(--color-primary-content);
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
}

button.submit-btn:hover:not(:disabled) {
    background-color: var(--mono-primary-dark, var(--color-primary-dark));
}

button.submit-btn:disabled {
    background-color: var(--mono-disabled-color, var(--color-base-300));
    color: var(--color-base-content-muted);
    cursor: not-allowed;
}

button.submit-btn.hidden,
.hidden {
    display: none;
}

.voted-message {
    margin-top: 1rem;
    font-size: 0.9rem;
    color: var(--mono-success-color, var(--color-success));
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Read-only state for already voted */
.option-label.voted {
    cursor: default;
    opacity: 0.8;
}

/* Print specific styles */
@media print {
    .poll-options {
        display: none !important;
    }
    .poll-container::after {
        content: "📊 (Interactive Poll - Print View)\nOptions are available in the interactive version.";
        display: block;
        margin-top: 1rem;
        padding: 1rem;
        border: 1px dashed #ccc;
        color: #666;
        text-align: center;
        background-color: #f5f5f5;
        border-radius: 8px;
    }
}
"""

with open("src/components/mono-poll/style.css", "w") as f:
    f.write(css)

print("Updated style.css")
