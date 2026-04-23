class MonoInteractiveElement extends HTMLElement {
    constructor() {
        super();
        this._authChangeListener = this._handleAuthChange.bind(this);
    }

    connectedCallback() {
        // 1. Initial State Check (Race Condition Mitigation)
        try {
            const savedAuth = localStorage.getItem("mono_auth");
            if (savedAuth) {
                const data = JSON.parse(savedAuth);
                if (data && data.user) {
                    this._triggerAuthStateChanged(data.user);
                } else {
                    this._triggerAuthStateChanged(null);
                }
            } else {
                 this._triggerAuthStateChanged(null);
            }
        } catch (e) {
            console.warn("Failed to read auth state from localStorage during initialization:", e);
            this._triggerAuthStateChanged(null); // Fallback to guest
        }

        // 2. Listen for global auth events broadcasted by mono-account
        window.addEventListener("mono-auth-changed", this._authChangeListener);
    }

    disconnectedCallback() {
        window.removeEventListener("mono-auth-changed", this._authChangeListener);
    }

    _handleAuthChange(event) {
        if (event && event.detail !== undefined) {
            this._triggerAuthStateChanged(event.detail.user || null);
        } else {
            this._triggerAuthStateChanged(null);
        }
    }

    _triggerAuthStateChanged(user) {
        if (typeof this.onAuthStateChanged === "function") {
            try {
                this.onAuthStateChanged(user);
            } catch (e) {
                console.error("Error in onAuthStateChanged hook:", e);
            }
        }
    }

    // Child classes can override this method to handle auth state changes.
    onAuthStateChanged(user) {
        // Default behavior is to do nothing, wait for child implementation.
    }
}
