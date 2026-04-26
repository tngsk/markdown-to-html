class MonoSync extends MonoBaseElement {
    constructor() {
        super();
    }

    connectedCallback() {
        super.mountTemplate('mono-sync-template');
        this.setupDataRecovery();
        this.setupFocusSync();
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
        // Listen for mono:vote and mono-data events bubbling up to document
        const handleDataEvent = (e) => {
            const data = {
                ...e.detail,
                environment: this.getEnvironmentContext(),
            };
            this.sendDataToServer(data);
        };
        document.addEventListener("mono:vote", handleDataEvent);
        document.addEventListener("mono-data", handleDataEvent);
    }

    async sendDataToServer(data) {
        const apiMeta = document.querySelector('meta[name="mono-api-url"]');
        const apiUrl = apiMeta ? apiMeta.content : null;
        if (!apiUrl) {
            console.info("💡 [Mono] スタンドアロンモードで動作しています。データはローカルにのみ保存されます。");
            return;
        }

        try {
            const response = await fetch(apiUrl + "/api/data", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error("Server responded with an error");
            }
        } catch (error) {
            console.info("💡 [Mono] サーバに接続できません（オフライン）。入力内容はブラウザに保存されているため、右下のボタンからJSONでダウンロードできます。");
        }
    }

    setupFocusSync() {
        const apiMeta = document.querySelector('meta[name="mono-api-url"]');
        const apiUrl = apiMeta ? apiMeta.content : null;
        if (!apiUrl) return;

        const urlParams = new URLSearchParams(window.location.search);
        const isHost = urlParams.get("role") === "host";

        try {
            if (isHost) {
                console.log("🟢 [Mono] リアルタイム同期を有効化しました（Role: Host）");
                this.setupHostObserver(apiUrl);
            } else {
                this.setupParticipantListener(apiUrl);
            }
        } catch (e) {
             console.info("💡 [Mono] 同期機能を初期化できませんでした。スタンドアロンで実行します。");
        }
    }

    setupHostObserver(apiUrl) {
        let lastTargetId = null;

        const observer = new IntersectionObserver((entries) => {
            // Find the most visible heading
            for (const entry of entries) {
                if (entry.isIntersecting && entry.target.id) {
                    if (lastTargetId !== entry.target.id) {
                        lastTargetId = entry.target.id;
                        this.broadcastFocus(apiUrl, lastTargetId);
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

    broadcastFocus(apiUrl, targetId) {
        fetch(apiUrl + "/api/sync", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ type: "focus", targetId })
        }).catch(err => {
            console.error("Focus broadcast error:", err);
        });
    }

    setupParticipantListener(apiUrl) {
        this.eventSource = new EventSource(apiUrl + "/api/sync/stream");

        this.eventSource.onopen = () => {
            console.log("🟢 [Mono] リアルタイム同期に接続しました（Role: Participant）");
        };

        this.eventSource.onerror = () => {
            console.info("💡 [Mono] 同期サーバとの接続が切断されました。");
        };

        this.eventSource.onmessage = (event) => {
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

if (!customElements.get("mono-sync")) {
    customElements.define("mono-sync", MonoSync);
}
// Automatically inject into page
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
        if (!document.querySelector("mono-sync")) {
            document.body.appendChild(document.createElement("mono-sync"));
        }
    });
} else {
    if (!document.querySelector("mono-sync")) {
        document.body.appendChild(document.createElement("mono-sync"));
    }
}
