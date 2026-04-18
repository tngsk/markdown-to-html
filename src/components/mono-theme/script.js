class MonoTheme extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });

        const template = document.getElementById('mono-theme-template');
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }

        this.container = this.shadowRoot.querySelector('.theme-switcher-container');
        this.select = this.shadowRoot.querySelector('#theme-select');
    }

    connectedCallback() {
        const theme = this.getAttribute('theme') || 'light';
        const showUi = this.getAttribute('show-ui') === 'true';

        // Apply theme to the whole document
        document.documentElement.setAttribute('data-theme', theme);

        if (showUi) {
            this.container.classList.remove('hidden');
            if (this.select) {
                this.select.value = theme;
                this.select.addEventListener('change', (e) => {
                    document.documentElement.setAttribute('data-theme', e.target.value);
                });
            }
        }
    }
}

if (!customElements.get('mono-theme')) {
    customElements.define('mono-theme', MonoTheme);
}
