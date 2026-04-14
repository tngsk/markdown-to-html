class SituSpacer extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    connectedCallback() {
        const template = document.getElementById("situ-spacer-template");
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }

        const width = this.getAttribute("width");
        const height = this.getAttribute("height");

        if (width) {
            this.style.width = width;
        }
        if (height) {
            this.style.height = height;
        }
    }
}

if (!customElements.get("situ-spacer")) {
    customElements.define("situ-spacer", SituSpacer);
}
