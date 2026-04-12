class SituTextfieldInput extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.placeholder = this.getAttribute("placeholder") || "";
        this.inputId = `textfield-${Math.random().toString(36).substr(2, 9)}`;
        this.debounceTimeout = null;
        this.storageUnavailable = false;
    }

    connectedCallback() {
        this.mountTemplate();
        this.setupEventListeners();
        this.restoreData();
    }

    mountTemplate() {
        const template = document.getElementById("situ-textfield-input-template");
        if (!template) {
            console.error("Template #situ-textfield-input-template not found.");
            return;
        }
        this.shadowRoot.appendChild(template.content.cloneNode(true));
        this.inputArea = this.shadowRoot.getElementById("textfield");
        this.inputArea.placeholder = this.placeholder;
        this.statusIndicator = this.shadowRoot.querySelector("[data-ref='statusIndicator']");

        try {
            const testKey = '__storage_test__';
            localStorage.setItem(testKey, testKey);
            localStorage.removeItem(testKey);
        } catch (e) {
            this.storageUnavailable = true;
            console.warn("Local Storage is not available. Input will not be persisted.", e);
        }
    }

    setupEventListeners() {
        if (this.inputArea) {
            this.inputArea.addEventListener("input", () => this.handleInput());
        }
    }

    getPageId() {
        return window.location.pathname || 'default-page';
    }

    getStorageKey() {
        // Prefix must be situ_ for situ-export to pick it up
        return `situ_textfield::${this.getPageId()}::${this.placeholder}`;
    }

    restoreData() {
        if (this.storageUnavailable || !this.inputArea) return;
        try {
            const stored = localStorage.getItem(this.getStorageKey());
            if (stored) {
                const data = JSON.parse(stored);
                if (data && data.value !== undefined) {
                    this.inputArea.value = data.value;
                }
            }
        } catch (e) {
            console.error("Failed to restore textfield data", e);
        }
    }

    handleInput() {
        if (this.storageUnavailable) return;
        if (this.debounceTimeout) {
            clearTimeout(this.debounceTimeout);
        }
        this.debounceTimeout = setTimeout(() => {
            this.saveData();
        }, 500);
    }

    saveData() {
        if (!this.inputArea) return;
        const value = this.inputArea.value;
        const data = {
            id: this.inputId,
            placeholder: this.placeholder,
            value: value,
            updated_at: new Date().toISOString()
        };
        try {
            localStorage.setItem(this.getStorageKey(), JSON.stringify(data));
            this.showSaveFeedback();
        } catch (e) {
            console.error("Failed to save textfield data", e);
        }
    }

    showSaveFeedback() {
        if (!this.statusIndicator) return;
        this.statusIndicator.textContent = "✓ Saved";
        this.statusIndicator.classList.remove("error");
        this.statusIndicator.classList.add("visible");
        setTimeout(() => {
            this.statusIndicator.classList.remove("visible");
        }, 2000);
    }
}

if (!customElements.get("situ-textfield-input")) {
    customElements.define("situ-textfield-input", SituTextfieldInput);
}
