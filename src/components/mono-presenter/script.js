class MonoPresenter extends MonoBaseElement {
    constructor() {
        super();
        this.channel = null;
        this.slides = [];
        this.currentSlideIndex = 0;
        this.notes = {};
        this.isPresenterMode = false;
        this.boundHandleKeyDown = this.handleKeyDown.bind(this);
        this.boundHandleScroll = this.handleScroll.bind(this);
        this.boundHandleHashChange = this.handleHashChange.bind(this);
        this.scrollTicking = false;
        this.isProgrammaticScroll = false;
        this.navScrollTimeout = null;
    }

    connectedCallback() {
        super.mountTemplate('mono-presenter-template');
        this.loadNotes();
        this.extractSlides();
        this.setupChannel();
        this.checkPresenterMode();
        this.setupEventListeners();
    }

    disconnectedCallback() {
        document.removeEventListener('keydown', this.boundHandleKeyDown);
        window.removeEventListener('scroll', this.boundHandleScroll);
        window.removeEventListener('hashchange', this.boundHandleHashChange);
        if (this.channel) {
            this.channel.close();
            this.channel = null;
        }
    }

    loadNotes() {
        const notesScript = document.getElementById('mono-speaker-notes');
        if (notesScript) {
            try {
                this.notes = JSON.parse(notesScript.textContent || '{}');
            } catch (e) {
                this.notes = {};
            }
        }
    }

    extractSlides() {
        const ignoredTags = new Set(['SCRIPT', 'TEMPLATE', 'STYLE', 'MONO-ZOOM', 'MONO-PRESENTER', 'MONO-BRUSH', 'MONO-SYNC', 'MONO-TOPIC-RAIL']);
        const elements = Array.from(document.body.children).filter(el => !ignoredTags.has(el.tagName));
        if (elements.length === 0) return;

        const hasExplicitHr = elements.some(el => el.tagName === 'HR');

        this.slides = [];
        let currentElements = [];
        let currentTitle = "スライド 1";
        let foundTitleForSlide = false;
        let slideIndex = 0;

        elements.forEach(el => {
            const tag = el.tagName;
            const isHr = (tag === 'HR');
            const isHeading = (!hasExplicitHr) && (tag === 'H1' || tag === 'H2');

            if (isHr || isHeading) {
                if (currentElements.length > 0) {
                    this.slides.push({
                        index: slideIndex,
                        title: currentTitle,
                        firstElement: currentElements[0],
                        note: this.notes[slideIndex] || this.notes[String(slideIndex)] || ''
                    });
                    slideIndex++;
                    currentElements = [];
                    currentTitle = `スライド ${slideIndex + 1}`;
                    foundTitleForSlide = false;
                }
                if (isHr) {
                    return;
                }
            }

            if (!foundTitleForSlide && (tag === 'H1' || tag === 'H2' || tag === 'H3' || tag === 'H4')) {
                currentTitle = el.textContent ? el.textContent.trim() : currentTitle;
                foundTitleForSlide = true;
            }

            currentElements.push(el);
        });

        if (currentElements.length > 0) {
            this.slides.push({
                index: slideIndex,
                title: currentTitle,
                firstElement: currentElements[0],
                note: this.notes[slideIndex] || this.notes[String(slideIndex)] || ''
            });
        }
    }

    checkPresenterMode() {
        const isPresenter = window.location.hash === '#presenter';
        this.isPresenterMode = isPresenter;

        if (isPresenter) {
            this.setAttribute('active', '');
            document.documentElement.setAttribute('data-mono-presenter-mode', 'true');
            this.updatePresenterPanel();
            // 親画面へ最新状態の初期同期を要求
            if (this.channel) {
                this.channel.postMessage({ type: 'request-init' });
            }
        } else {
            this.removeAttribute('active');
            document.documentElement.removeAttribute('data-mono-presenter-mode');
        }
    }

    handleHashChange() {
        this.checkPresenterMode();
    }

    setupChannel() {
        this.boundHandleIncomingMessage = (event) => {
            const data = event.data;
            if (!data) return;

            if (data.type === 'navigate') {
                this.navigateToSlide(data.index, false);
            } else if (data.type === 'state-sync') {
                if (this.isPresenterMode && data.currentIndex !== undefined) {
                    this.currentSlideIndex = data.currentIndex;
                    this.updatePresenterPanel();
                }
            } else if (data.type === 'request-init') {
                if (!this.isPresenterMode) {
                    this.syncToPresenter();
                }
            }
        };

        try {
            this.channel = new BroadcastChannel('mono-presenter-channel');
            this.channel.onmessage = this.boundHandleIncomingMessage;
        } catch (e) {
            // BroadcastChannel非対応環境
        }

        window.addEventListener('message', this.boundHandleIncomingMessage);
    }

    setupEventListeners() {
        const btn = this.shadowRoot.getElementById('presenter-btn');
        if (btn) {
            btn.addEventListener('click', () => this.openPresenterWindow());
        }

        const panel = this.shadowRoot.getElementById('presenter-panel');
        if (panel) {
            panel.addEventListener('wheel', (e) => {
                const body = this.shadowRoot.querySelector('.panel-body');
                if (!body) return;

                const isScrollable = body.scrollHeight > body.clientHeight;
                if (!isScrollable) {
                    e.preventDefault();
                    e.stopPropagation();
                    return;
                }

                const atTop = body.scrollTop <= 0 && e.deltaY < 0;
                const atBottom = (body.scrollTop + body.clientHeight >= body.scrollHeight - 1) && e.deltaY > 0;
                if (atTop || atBottom) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }, { passive: false });
        }

        document.addEventListener('keydown', this.boundHandleKeyDown);
        window.addEventListener('scroll', this.boundHandleScroll, { passive: true });
        window.addEventListener('hashchange', this.boundHandleHashChange);
    }

    handleScroll() {
        if (this.isProgrammaticScroll) return;
        if (this.scrollTicking) return;
        this.scrollTicking = true;
        requestAnimationFrame(() => {
            if (this.isProgrammaticScroll) {
                this.scrollTicking = false;
                return;
            }
            this.updateActiveSlideFromScroll();
            this.scrollTicking = false;
        });
    }

    updateActiveSlideFromScroll() {
        if (this.slides.length === 0) return;
        const scrollY = window.scrollY;
        const viewportHeight = window.innerHeight;
        const focalPoint = viewportHeight * 0.35;

        let bestIndex = 0;

        if (scrollY < 60) {
            bestIndex = 0;
        } else {
            for (let i = 0; i < this.slides.length; i++) {
                const slide = this.slides[i];
                if (!slide.firstElement) continue;
                const top = slide.firstElement.getBoundingClientRect().top;
                const nextSlide = this.slides[i + 1];
                const nextTop = (nextSlide && nextSlide.firstElement)
                    ? nextSlide.firstElement.getBoundingClientRect().top
                    : Infinity;

                if (top <= focalPoint + 50 && focalPoint < nextTop + 50) {
                    bestIndex = i;
                    break;
                }
                if (i === this.slides.length - 1 && top <= focalPoint + 100) {
                    bestIndex = i;
                }
            }
        }

        if (bestIndex !== this.currentSlideIndex) {
            this.currentSlideIndex = Math.min(bestIndex, this.slides.length - 1);
            if (this.isPresenterMode) {
                this.updatePresenterPanel();
                // スライド境界を跨いだ際、投影画面へスライド単位で同期通知
                const payload = {
                    type: 'navigate',
                    index: this.currentSlideIndex
                };
                if (this.channel) {
                    try { this.channel.postMessage(payload); } catch (e) {}
                }
                if (window.opener && !window.opener.closed) {
                    try { window.opener.postMessage(payload, '*'); } catch (e) {}
                }
            }
        }
    }

    handleKeyDown(e) {
        const activeEl = document.activeElement;
        const isEditable = activeEl && (
            activeEl.tagName === 'INPUT' ||
            activeEl.tagName === 'TEXTAREA' ||
            activeEl.isContentEditable
        );
        if (isEditable) return;

        if (this.isPresenterMode) {
            // プレゼンターウィンドウ内のスライド移動
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown' || e.key === 'j' || e.key === 'J') {
                this.nextSlide();
                e.preventDefault();
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp' || e.key === 'k' || e.key === 'K') {
                this.prevSlide();
                e.preventDefault();
            }
        } else {
            // 投射画面でのプレゼンターウィンドウ起動
            if (e.key === 'p' || e.key === 'P') {
                this.openPresenterWindow();
                e.preventDefault();
            }
        }
    }

    nextSlide() {
        if (this.currentSlideIndex < this.slides.length - 1) {
            this.navigateToSlide(this.currentSlideIndex + 1, true);
        }
    }

    prevSlide() {
        if (this.currentSlideIndex > 0) {
            this.navigateToSlide(this.currentSlideIndex - 1, true);
        }
    }

    navigateToSlide(targetIndex, broadcast = true) {
        if (targetIndex < 0 || targetIndex >= this.slides.length) return;
        this.currentSlideIndex = targetIndex;

        // プログラマティックスクロールによる誤検知を抑制
        this.isProgrammaticScroll = true;
        clearTimeout(this.navScrollTimeout);
        this.navScrollTimeout = setTimeout(() => {
            this.isProgrammaticScroll = false;
        }, 700);

        const targetSlide = this.slides[targetIndex];
        if (targetSlide && targetSlide.firstElement) {
            targetSlide.firstElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        if (this.isPresenterMode) {
            this.updatePresenterPanel();
        }

        if (broadcast) {
            const payload = {
                type: 'navigate',
                index: targetIndex
            };
            if (this.channel) {
                try { this.channel.postMessage(payload); } catch (e) {}
            }
            if (window.opener && !window.opener.closed) {
                try { window.opener.postMessage(payload, '*'); } catch (e) {}
            }
        }
    }

    syncToPresenter() {
        const payload = {
            type: 'state-sync',
            currentIndex: this.currentSlideIndex,
            totalSlides: this.slides.length
        };

        if (this.channel) {
            try { this.channel.postMessage(payload); } catch (e) {}
        }
    }

    updatePresenterPanel() {
        const indicator = this.shadowRoot.getElementById('slide-indicator');
        const content = this.shadowRoot.getElementById('script-content');
        if (!indicator || !content) return;

        const total = this.slides.length || 1;
        const current = this.currentSlideIndex + 1;
        indicator.textContent = `スライド ${current} / ${total}`;

        const slide = this.slides[this.currentSlideIndex];
        const noteText = slide && slide.note ? slide.note.trim() : '';

        if (noteText) {
            content.textContent = noteText;
            content.classList.remove('script-empty');
        } else {
            content.textContent = '（トークスクリプトはありません）';
            content.classList.add('script-empty');
        }

        const panelBody = this.shadowRoot.querySelector('.panel-body');
        if (panelBody) {
            panelBody.scrollTop = 0;
        }
    }

    openPresenterWindow() {
        const baseHref = window.location.href.split('#')[0];
        const presenterUrl = `${baseHref}#presenter`;

        const width = 1200;
        const height = 800;
        const left = window.screen.width ? (window.screen.width - width) / 2 : 50;
        const top = window.screen.height ? (window.screen.height - height) / 2 : 50;

        const win = window.open(
            presenterUrl,
            'mono_presenter_view',
            `width=${width},height=${height},left=${left},top=${top},menubar=no,toolbar=no,location=no,status=no,resizable=yes`
        );

        if (!win) {
            alert('ポップアップウィンドウが開けませんでした。ブラウザのポップアップブロックを許可してください。');
            return;
        }

        win.focus();
        setTimeout(() => this.syncToPresenter(), 300);
    }
}

if (!customElements.get('mono-presenter')) {
    customElements.define('mono-presenter', MonoPresenter);
}

// DOM読み込み完了時に自動配置
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!document.querySelector('mono-presenter')) {
            document.body.appendChild(document.createElement('mono-presenter'));
        }
    });
} else {
    if (!document.querySelector('mono-presenter')) {
        document.body.appendChild(document.createElement('mono-presenter'));
    }
}
