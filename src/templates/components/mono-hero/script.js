class MonoHero extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        const template = document.getElementById('mono-hero-template');
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }
    }

    connectedCallback() {
        const container = this.shadowRoot.getElementById('hero-container');
        if (!container) return;

        // Apply background image
        const image = this.getAttribute('image');
        if (image) {
            this.style.setProperty('--hero-bg-image', `url('${image}')`);
            container.style.backgroundImage = `url('${image}')`;
        }

        // Apply background mode (cover, fit/contain)
        const mode = this.getAttribute('mode');
        if (mode === 'fit' || mode === 'contain') {
            this.style.setProperty('--hero-bg-mode', 'contain');
            container.style.backgroundSize = 'contain';
        } else {
            this.style.setProperty('--hero-bg-mode', 'cover');
            container.style.backgroundSize = 'cover';
        }

        // Apply background color
        const bgColor = this.getAttribute('bg-color');
        if (bgColor) {
            this.style.setProperty('--hero-bg-color', bgColor);
            container.style.backgroundColor = bgColor;
        }

        // Apply text color
        const textColor = this.getAttribute('text-color');
        if (textColor) {
            this.style.setProperty('--hero-text-color', textColor);
            container.style.color = textColor;
        }
    }
}

customElements.define('mono-hero', MonoHero);
