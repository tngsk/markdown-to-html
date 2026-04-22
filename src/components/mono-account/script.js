class MonoAccount extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this.user = null;
        this.refs = {};
    }

    connectedCallback() {
        this.mountTemplate();
        this.initializeAuth();
    }

    mountTemplate() {
        const template = document.getElementById("mono-account-template");
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
            this.shadowRoot.querySelectorAll("[data-ref]").forEach(el => {
                this.refs[el.dataset.ref] = el;
            });

            if (this.refs.actionBtn) {
                this.refs.actionBtn.addEventListener("click", () => this.toggleAuth());
            }
        }
    }

    initializeAuth() {
        try {
            const savedAuth = localStorage.getItem("mono_auth");
            if (savedAuth) {
                const data = JSON.parse(savedAuth);
                if (data && data.user) {
                    this.user = data.user;
                }
            }
        } catch (e) {
            console.info("アカウント機能はオフラインです", e);
            this.user = null;
        }

        this.updateView();
        this.broadcastAuthState();
    }

    toggleAuth() {
        if (this.user) {
            // Logout
            this.user = null;
            try {
                localStorage.removeItem("mono_auth");
            } catch(e) {
                console.info("Failed to remove auth state", e);
            }
        } else {
            // Mock Login
            this.user = {
                id: "user-" + Math.random().toString(36).substring(2, 9),
                name: "Test User",
                token: "mock-jwt-token"
            };
            try {
                localStorage.setItem("mono_auth", JSON.stringify({ user: this.user }));
            } catch(e) {
                console.info("Failed to save auth state", e);
            }
        }

        this.updateView();
        this.broadcastAuthState();
    }

    updateView() {
        if (!this.refs.status || !this.refs.actionBtn) return;

        if (this.user) {
            this.refs.status.textContent = `Logged in as: ${this.user.name}`;
            this.refs.actionBtn.textContent = "Logout";
        } else {
            this.refs.status.textContent = "Guest Mode";
            this.refs.actionBtn.textContent = "Login";
        }
    }

    broadcastAuthState() {
        const payload = { user: this.user };
        const event = new CustomEvent("mono-auth-changed", {
            detail: payload,
            bubbles: true,
            composed: true,
        });
        window.dispatchEvent(event);
    }
}

if (!customElements.get("mono-account")) {
    customElements.define("mono-account", MonoAccount);
}
