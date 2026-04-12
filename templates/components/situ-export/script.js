class SituExport extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
    }

    connectedCallback() {
        this.mountTemplate();
        this.setupEventListeners();
    }

    mountTemplate() {
        const style = document.createElement("style");
        style.textContent = `{COMPONENTS_CSS}`;
        this.shadowRoot.appendChild(style);

        const container = document.createElement("div");
        container.innerHTML = `
        <div class="situ-export-container">
            <button id="situ-export-fab" class="fab" title="Export Data">
                <svg viewBox="0 0 24 24" width="24" height="24"><path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
            </button>
            <div id="situ-export-menu" class="menu hidden">
                <button id="situ-export-download">Download JSON</button>
                <button id="situ-export-sync">Sync to Server</button>
            </div>
        </div>
        `;
        this.shadowRoot.appendChild(container);
    }

    collectData() {
        const data = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith("situ_")) {
                try {
                    data[key] = JSON.parse(localStorage.getItem(key));
                } catch (e) {
                    data[key] = localStorage.getItem(key);
                }
            }
        }
        return data;
    }

    setupEventListeners() {
        const fab = this.shadowRoot.getElementById("situ-export-fab");
        const menu = this.shadowRoot.getElementById("situ-export-menu");
        const btnDownload = this.shadowRoot.getElementById("situ-export-download");
        const btnSync = this.shadowRoot.getElementById("situ-export-sync");

        fab.addEventListener("click", () => {
            menu.classList.toggle("hidden");
        });

        btnDownload.addEventListener("click", () => {
            const data = this.collectData();
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `export_${new Date().getTime()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            menu.classList.add("hidden");
        });

        btnSync.addEventListener("click", async () => {
            const data = this.collectData();
            const apiMeta = document.querySelector('meta[name="situ-api-url"]');
            const apiUrl = apiMeta ? apiMeta.content : null;
            if (!apiUrl) {
                alert("サーバのURLが設定されていません。データを保存するには「Download JSON」を使用してください。");
                console.info("💡 [Interactive-MD] スタンドアロンモードです。手動でJSONをダウンロードしてください。");
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
                if (response.ok) {
                    alert("✅ データをサーバに同期しました！");
                } else {
                    alert("❌ サーバへの同期に失敗しました。\n\nオフラインの可能性があります。「Download JSON」からローカルに保存してください。");
                    console.info("💡 [Interactive-MD] サーバエラー。ステータス: " + response.statusText);
                }
            } catch (error) {
                alert("❌ サーバへの同期に失敗しました。\n\nオフラインの可能性があります。「Download JSON」からローカルに保存してください。");
                console.info("💡 [Interactive-MD] オフラインまたはサーバ未起動です。");
            }
            menu.classList.add("hidden");
        });
    }
}

if (!customElements.get("situ-export")) {
    customElements.define("situ-export", SituExport);
}