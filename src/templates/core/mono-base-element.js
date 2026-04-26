class MonoBaseElement extends HTMLElement {
    constructor(options = { shadowMode: 'open' }) {
        super();
        this.refs = {};
        this._isMounted = false; // 二重マウント防止用フラグ

        if (options && options.shadowMode) {
            this.attachShadow({ mode: options.shadowMode });
        }
    }

    /**
     * テンプレートをマウントし、data-ref要素をキャッシュする。
     * @param {string} templateId
     */
    mountTemplate(templateId) {
        if (this._isMounted) return;

        const template = document.getElementById(templateId);
        if (!template) {
            console.error(`[Mono] Template #${templateId} not found.`);
            return;
        }

        const root = this.shadowRoot || this;
        root.appendChild(template.content.cloneNode(true));

        // data-refのキャッシュ（セキュリティのためtextContent等の操作を想定）
        root.querySelectorAll("[data-ref]").forEach((el) => {
            this.refs[el.dataset.ref] = el;
        });

        this._isMounted = true;
    }
}
