class MonoFlipcard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.toggleFlip = this.toggleFlip.bind(this);
    }

    connectedCallback() {
        const template = document.getElementById("mono-flipcard-template");
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }

        const frontText = this.getAttribute("front") || "";
        const backText = this.getAttribute("back") || "";

        const frontEl = this.shadowRoot.getElementById("front-text");
        const backEl = this.shadowRoot.getElementById("back-text");

        if (frontEl) frontEl.textContent = frontText;
        if (backEl) backEl.textContent = backText;

        this.addEventListener('click', this.toggleFlip);
    }

    disconnectedCallback() {
        this.removeEventListener('click', this.toggleFlip);
    }

    toggleFlip() {
        if (this.hasAttribute('flipped')) {
            this.removeAttribute('flipped');
        } else {
            this.setAttribute('flipped', '');
        }
    }
}

if (!customElements.get("mono-flipcard")) {
    customElements.define("mono-flipcard", MonoFlipcard);
}
