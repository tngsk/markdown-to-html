class MonoTopicRail extends MonoBaseElement {
    constructor() {
        super();
        this.topics = [];
        this.currentActiveIndex = -1;
        this.onScrollBound = this.onScroll.bind(this);
        this.onResizeBound = this.onResize.bind(this);
        this.resizeTimer = null;
    }

    connectedCallback() {
        this.mountTemplate("template-mono-topic-rail");
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => this.initRail());
        } else {
            setTimeout(() => this.initRail(), 30);
        }

        // 画像やフォント読み込み完了時の座標再計算
        window.addEventListener("load", () => {
            this.renderSegments();
            this.updateActiveBadge();
        });
        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(() => {
                this.renderSegments();
                this.updateActiveBadge();
            });
        }
    }

    disconnectedCallback() {
        window.removeEventListener("scroll", this.onScrollBound);
        document.removeEventListener("scroll", this.onScrollBound);
        window.removeEventListener("resize", this.onResizeBound);
        if (this.resizeTimer) clearTimeout(this.resizeTimer);
    }

    getAbsoluteTop(element) {
        let top = 0;
        let current = element;
        while (current) {
            top += current.offsetTop || 0;
            current = current.offsetParent;
        }
        return top;
    }

    initRail() {
        // 見出しの .topic または .section を走査
        const elements = Array.from(
            document.querySelectorAll(
                "h1.topic, h2.topic, h3.topic, h4.topic, h5.topic, h6.topic, .topic, h1.section, h2.section, h3.section, .section"
            )
        );

        const uniqueElements = Array.from(new Set(elements));
        if (uniqueElements.length === 0) return;

        // Doc 5-tone 高視認性カラー配列
        const toneVars = [
            "#eab308", // Yellow
            "#ec4899", // Pink
            "#10b981", // Green
            "#06b6d4", // Cyan
            "#f97316"  // Orange
        ];

        this.topics = uniqueElements.map((el, i) => {
            const title = el.textContent.trim() || `Topic ${i + 1}`;
            const color = toneVars[i % toneVars.length];
            return { element: el, title, color, index: i, top: 0 };
        });

        this.renderSegments();
        this.setupEventListeners();
        this.updateActiveBadge();
    }

    renderSegments() {
        const container = this.shadowRoot ? this.shadowRoot.querySelector(".topic-scroll-rail-container") : null;
        if (!container || !this.topics.length) return;

        // 各トピックの絶対座標を再計算
        this.topics.forEach(t => {
            t.top = this.getAbsoluteTop(t.element);
        });

        container.innerHTML = "";
        const totalHeight = Math.max(
            document.documentElement.scrollHeight,
            document.body.scrollHeight
        );

        for (let i = 0; i < this.topics.length; i++) {
            const current = this.topics[i];
            const startTop = current.top;

            let endTop;
            if (i < this.topics.length - 1) {
                endTop = this.topics[i + 1].top;
            } else {
                endTop = totalHeight;
            }

            const segHeight = Math.max(0, endTop - startTop);

            const seg = document.createElement("div");
            seg.className = "topic-scroll-segment";
            seg.style.top = `${startTop}px`;
            seg.style.height = `${segHeight}px`;
            seg.style.setProperty("--segment-color", current.color);
            container.appendChild(seg);
        }
    }

    setupEventListeners() {
        window.addEventListener("scroll", this.onScrollBound, { passive: true });
        document.addEventListener("scroll", this.onScrollBound, { passive: true });
        window.addEventListener("resize", this.onResizeBound, { passive: true });

        // 右上バッジをクリックで現在のセクション先頭へスムーズスクロール
        const badge = this.shadowRoot ? this.shadowRoot.querySelector(".topic-current-badge") : null;
        if (badge) {
            badge.addEventListener("click", () => {
                if (this.currentActiveIndex >= 0 && this.topics[this.currentActiveIndex]) {
                    this.topics[this.currentActiveIndex].element.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            });
        }
    }

    onScroll() {
        this.updateActiveBadge();
    }

    onResize() {
        if (this.resizeTimer) clearTimeout(this.resizeTimer);
        this.resizeTimer = setTimeout(() => {
            this.renderSegments();
            this.updateActiveBadge();
        }, 100);
    }

    updateActiveBadge() {
        if (!this.topics.length) return;

        const badge = this.shadowRoot ? this.shadowRoot.querySelector(".topic-current-badge") : null;
        const badgeTitle = this.shadowRoot ? this.shadowRoot.querySelector(".topic-badge-title") : null;
        if (!badge || !badgeTitle) return;

        const scrollY = window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
        const focalPoint = scrollY + window.innerHeight * 0.35;

        let activeIndex = -1;
        for (let i = 0; i < this.topics.length; i++) {
            if (this.topics[i].top <= focalPoint) {
                activeIndex = i;
            } else {
                break;
            }
        }

        this.currentActiveIndex = activeIndex;

        if (activeIndex >= 0) {
            const activeTopic = this.topics[activeIndex];
            badgeTitle.textContent = activeTopic.title;
            badge.style.setProperty("--active-topic-color", activeTopic.color);
            badge.classList.add("visible");
        } else {
            // 最初のトピック見出しに到達する前（タイトル等）は非表示
            badge.classList.remove("visible");
        }
    }
}

if (typeof customElements !== "undefined") {
    customElements.define("mono-topic-rail", MonoTopicRail);
}
