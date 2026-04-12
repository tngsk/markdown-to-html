class SituSync extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    connectedCallback() {
        this.mountTemplate();
        this.setupDataRecovery();
        this.setupFocusSync();
    }

    mountTemplate() {
        const template = document.getElementById("situ-sync-template");
        if (template) {
            this.shadowRoot.appendChild(template.content.cloneNode(true));
        }
    }

    getEnvironmentContext() {
        return {
            userAgent: navigator.userAgent,
            windowWidth: window.innerWidth,
            windowHeight: window.innerHeight,
            url: window.location.href,
        };
    }

    setupDataRecovery() {
        // Listen for situ:vote events bubbling up to document
        document.addEventListener("situ:vote", (e) => {
            const data = {
                ...e.detail,
                environment: this.getEnvironmentContext(),
            };
            this.sendDataToServer(data);
        });
    }

    async sendDataToServer(data) {
        const apiUrl = window.SITU_API_URL;
        if (!apiUrl) {
            console.warn("SITU_API_URL not configured. Data not sent.");
            return;
        }

        try {
            await fetch(apiUrl + "/api/data", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error("Data Recovery failed:", error);
        }
    }

    setupFocusSync() {
        const wsUrl = window.SITU_WS_URL;
        if (!wsUrl) return;

        const urlParams = new URLSearchParams(window.location.search);
        const isHost = urlParams.get("role") === "host";

        this.ws = new WebSocket(wsUrl + "/ws/sync");

        this.ws.onopen = () => {
            console.log("WebSocket connected. Host:", isHost);
        };

        if (isHost) {
            this.setupHostObserver();
        } else {
            this.setupParticipantListener();
        }
    }

    setupHostObserver() {
        let lastTargetId = null;

        const observer = new IntersectionObserver((entries) => {
            // Find the most visible heading
            for (const entry of entries) {
                if (entry.isIntersecting && entry.target.id) {
                    if (lastTargetId !== entry.target.id) {
                        lastTargetId = entry.target.id;
                        this.broadcastFocus(lastTargetId);
                    }
                    break;
                }
            }
        }, { threshold: 0.5 });

        // Observe h1, h2, h3 tags
        document.querySelectorAll("h1, h2, h3").forEach(el => {
            if (el.id) observer.observe(el);
        });
    }

    broadcastFocus(targetId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: "focus", targetId }));
        }
    }

    setupParticipantListener() {
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "focus" && data.targetId) {
                    const el = document.getElementById(data.targetId);
                    if (el) {
                        el.scrollIntoView({ behavior: "smooth" });
                    }
                }
            } catch (e) {
                console.error("Focus Sync error:", e);
            }
        };
    }
}

if (!customElements.get("situ-sync")) {
    customElements.define("situ-sync", SituSync);
}
// Automatically inject into page
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        if (!document.querySelector("situ-sync")) {
            document.body.appendChild(document.createElement("situ-sync"));
        }
    });
} else {
    if (!document.querySelector("situ-sync")) {
        document.body.appendChild(document.createElement("situ-sync"));
    }
}
