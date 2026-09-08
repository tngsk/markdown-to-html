if (typeof MonoBaseElement === "undefined") {
    var MonoBaseElement = typeof HTMLElement !== "undefined" ? HTMLElement : class {};
}

class MonoTopicRail extends MonoBaseElement {
    constructor() {
        super();
        this.topics = [];
        this.observer = null;
        this.onScrollBound = this.onScroll.bind(this);
    }

    connectedCallback() {
        this.mountTemplate("template-mono-topic-rail");
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => this.initRail());
        } else {
            setTimeout(() => this.initRail(), 0);
        }
    }

    disconnectedCallback() {
        if (this.observer) {
            this.observer.disconnect();
        }
        window.removeEventListener("scroll", this.onScrollBound);
    }

    initRail() {
        const container = this.shadowRoot ? this.shadowRoot.querySelector(".topic-rail-container") : null;
        if (!container) return;

        // 見出しの .topic または .section を走査
        const elements = Array.from(
            document.querySelectorAll(
                "h1.topic, h2.topic, h3.topic, h4.topic, h5.topic, h6.topic, .topic, h1.section, h2.section, h3.section, .section"
            )
        );

        // 重複除外
        const uniqueElements = Array.from(new Set(elements));
        if (uniqueElements.length === 0) return;

        // Doc 5-tone CSS変数の配列
        const toneVars = [
            "var(--mono-marker-yellow)",
            "var(--mono-marker-pink)",
            "var(--mono-marker-green)",
            "var(--mono-marker-cyan)",
            "var(--mono-marker-orange)"
        ];

        container.innerHTML = "";
        this.topics = uniqueElements.map((el, i) => {
            const title = el.textContent.trim() || `Topic ${i + 1}`;
            const color = toneVars[i % toneVars.length];

            const seg = document.createElement("div");
            seg.className = "topic-rail-segment";
            seg.style.setProperty("--segment-color", color);
            seg.setAttribute("data-title", title);
            seg.style.flex = "1";

            seg.addEventListener("click", () => {
                el.scrollIntoView({ behavior: "smooth", block: "start" });
            });

            container.appendChild(seg);
            return { element: el, segment: seg, index: i };
        });

        this.setupObserver();
        this.updateActive();
    }

    setupObserver() {
        window.addEventListener("scroll", this.onScrollBound, { passive: true });
    }

    onScroll() {
        this.updateActive();
    }

    updateActive() {
        if (!this.topics.length) return;

        const scrollY = window.scrollY || window.pageYOffset;
        const viewportMiddle = scrollY + window.innerHeight * 0.35;

        let activeIndex = 0;
        for (let i = 0; i < this.topics.length; i++) {
            const rect = this.topics[i].element.getBoundingClientRect();
            const top = rect.top + scrollY;
            if (top <= viewportMiddle) {
                activeIndex = i;
            } else {
                break;
            }
        }

        this.topics.forEach((t, i) => {
            if (i === activeIndex) {
                t.segment.classList.add("active");
            } else {
                t.segment.classList.remove("active");
            }
        });
    }
}

if (typeof customElements !== "undefined") {
    customElements.define("mono-topic-rail", MonoTopicRail);
}
