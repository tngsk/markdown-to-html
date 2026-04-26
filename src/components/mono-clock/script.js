class MonoClock extends MonoBaseElement {
    constructor() {
        super();
        this._intervalId = null;
    }

    connectedCallback() {
        this.mountTemplate('mono-clock-template');

        this.clockElement = this.shadowRoot.querySelector('.clock-display');

        const display = this.getAttribute('display');
        if (display && display !== "block" && display !== "inline") {
            this.style.display = display;
        }

        this.format = this.getAttribute('format') || 'HH:mm:ss';

        this.updateClock();
        this._intervalId = setInterval(() => this.updateClock(), 1000);
    }

    disconnectedCallback() {
        if (this._intervalId) {
            clearInterval(this._intervalId);
            this._intervalId = null;
        }
    }

    updateClock() {
        if (!this.clockElement) return;

        const now = new Date();
        const tokens = {
            'YYYY': now.getFullYear(),
            'YY': String(now.getFullYear()).slice(-2),
            'MM': String(now.getMonth() + 1).padStart(2, '0'),
            'DD': String(now.getDate()).padStart(2, '0'),
            'HH': String(now.getHours()).padStart(2, '0'),
            'mm': String(now.getMinutes()).padStart(2, '0'),
            'ss': String(now.getSeconds()).padStart(2, '0')
        };

        let output = this.format;
        for (const [key, value] of Object.entries(tokens)) {
            output = output.replace(new RegExp(key, 'g'), value);
        }

        this.clockElement.textContent = output;
    }
}

if (!customElements.get('mono-clock')) {
    customElements.define('mono-clock', MonoClock);
}
