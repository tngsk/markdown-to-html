class MonoSpacer extends MonoBaseElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.mountTemplate('mono-spacer-template');

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

if (!customElements.get("mono-spacer")) {
    customElements.define("mono-spacer", MonoSpacer);
}
