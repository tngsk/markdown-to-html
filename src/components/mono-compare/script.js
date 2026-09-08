if (typeof MonoBaseElement === "undefined") {
    var MonoBaseElement = typeof HTMLElement !== "undefined" ? HTMLElement : class {};
}

class MonoCompare extends MonoBaseElement {
    constructor() {
        super();
    }

    connectedCallback() {
        this.mountTemplate("template-mono-compare");
        this.resolveMode();
    }

    resolveMode() {
        if (!this.getAttribute("mode")) {
            // スロット内の子要素数をカウントして自動判別
            const children = Array.from(this.children).filter(
                (el) => el.nodeType === Node.ELEMENT_NODE
            );
            if (children.length === 2) {
                this.setAttribute("mode", "2");
            } else if (children.length === 3) {
                this.setAttribute("mode", "3");
            } else {
                this.setAttribute("mode", "2");
            }
        }
    }
}

if (typeof customElements !== "undefined") {
    customElements.define("mono-compare", MonoCompare);
}
