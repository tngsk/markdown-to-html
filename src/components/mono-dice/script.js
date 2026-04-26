class MonoDice extends MonoInteractiveElement {
    constructor() {
        super();

        const facesAttr = this.getAttribute("faces") || this.getAttribute("number");
        this.faces = facesAttr ? parseInt(facesAttr, 10) : 6;
        if (isNaN(this.faces) || this.faces < 2) {
            this.faces = 6;
        }

        this.isRolling = false;
    }

    connectedCallback() {
        super.mountTemplate('mono-dice-template');
        this.setupEventListeners();
    }

    setupEventListeners() {
        if (this.refs.dice) {
            this.refs.dice.addEventListener("click", () => this.roll());
        }
    }

    roll() {
        if (this.isRolling) return;
        this.isRolling = true;

        if (this.refs.dice) {
            this.refs.dice.classList.add("rolling");
        }

        if (this.refs.number) {
            this.refs.number.textContent = "?";
        }

        let rollInterval = setInterval(() => {
            if (this.refs.number) {
                this.refs.number.textContent = Math.floor(Math.random() * this.faces) + 1;
            }
        }, 100);

        setTimeout(() => {
            clearInterval(rollInterval);
            this.isRolling = false;

            const result = Math.floor(Math.random() * this.faces) + 1;

            if (this.refs.dice) {
                this.refs.dice.classList.remove("rolling");
            }
            if (this.refs.number) {
                this.refs.number.textContent = result;
            }
        }, 800);
    }
}

if (!customElements.get("mono-dice")) {
    customElements.define("mono-dice", MonoDice);
}