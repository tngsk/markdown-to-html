class SituIcon extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
    }

    connectedCallback() {
        // Clone the template
        const template = document.getElementById('situ-icon-template');
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        } else {
            console.error('situ-icon-template not found');
            return;
        }

        const iconSpan = this.shadowRoot.querySelector('.material-symbols-outlined');
        const name = this.getAttribute('name');
        if (name && iconSpan) {
            iconSpan.textContent = name;
        }

        // Apply styles based on attributes
        const size = this.getAttribute('size');
        if (size) {
            this.style.fontSize = size;
        }

        const color = this.getAttribute('color');
        if (color) {
            this.style.color = color;
        }

        const display = this.getAttribute('display');
        if (display && display !== "block" && display !== "inline") {
            this.style.display = display;
        }
    }
}

// Register the custom element
if (!customElements.get('situ-icon')) {
    customElements.define('situ-icon', SituIcon);
}
