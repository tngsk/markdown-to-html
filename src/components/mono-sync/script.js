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
        const wsMeta = document.querySelector('meta[name="mono-ws-url"]');
        const wsUrl = wsMeta ? wsMeta.content : null;
        if (!wsUrl) return;

        const urlParams = new URLSearchParams(window.location.search);
        const isHost = urlParams.get("role") === "host";

        try {
            this.ws = new WebSocket(wsUrl + "/ws/sync");

            this.ws.onopen = () => {
                console.log("🟢 [Mono] リアルタイム同期に接続しました（Role: " + (isHost ? "Host" : "Participant") + "）");
            };

            this.ws.onerror = () => {
                console.info("💡 [Mono] 同期サーバが見つかりません。ドキュメントは引き続き単独で閲覧可能です。");
            };

            this.ws.onclose = () => {
                // Connection closed messages can be noisy if the server shuts down, so we use info.
                console.info("💡 [Mono] 同期サーバとの接続が終了しました。");
            };

            if (isHost) {
                this.setupHostObserver();
            } else {
                this.setupParticipantListener();
            }
        } catch (e) {
             console.info("💡 [Mono] 同期機能を初期化できませんでした。スタンドアロンで実行します。");
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
