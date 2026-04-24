class MonoBadge extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });

        const template = document.getElementById('mono-badge-template');
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }
    }

    connectedCallback() {
        this.render();
    }

    static get observedAttributes() {
        return ['color', 'soft', 'outline'];
    }

    attributeChangedCallback() {
        this.render();
    }

    render() {
        // apply classes based on attributes to the wrapper inside the template
        const wrapper = this.shadowRoot.querySelector('.mono-badge');
        if (!wrapper) return;

        // Reset classes
        wrapper.className = 'mono-badge';

        const color = this.getAttribute('color');
        if (color) {
            wrapper.classList.add(`mono-badge-${color}`);
        }

        if (this.hasAttribute('soft')) {
            wrapper.classList.add('mono-badge-soft');
        }

        if (this.hasAttribute('outline')) {
            wrapper.classList.add('mono-badge-outline');
        }
    }
}

customElements.define('mono-badge', MonoBadge);
