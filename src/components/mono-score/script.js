class MonoScore extends HTMLElement {
    constructor() {
        super();
    }

    async connectedCallback() {
        const template = document.getElementById('mono-score-template');
        if (template && !this.querySelector('.score-container')) {
            this.appendChild(template.content.cloneNode(true));
        }

        const container = this.querySelector('.score-container') || this;

        // Ensure VexFlow is loaded
        await this.loadVexFlow();

        this.renderScore(container);
    }

    async loadVexFlow() {
        if (window.Vex && window.Vex.Flow) return;

        // Cache the promise so multiple components don't inject multiple scripts
        if (!window.__vexFlowLoadingPromise) {
            window.__vexFlowLoadingPromise = new Promise((resolve, reject) => {
                const script = document.createElement('script');
                script.src = "https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js";
                script.onload = () => {
                    if (window.Vex && window.Vex.Flow) {
                        resolve();
                    } else {
                        setTimeout(() => {
                            if (window.Vex && window.Vex.Flow) {
                                resolve();
                            } else {
                                console.error("VexFlow failed to load correctly on window");
                                reject(new Error("VexFlow not on window"));
                            }
                        }, 100);
                    }
                };
                script.onerror = reject;
                document.head.appendChild(script);
            });
        }

        return window.__vexFlowLoadingPromise;
    }

    renderScore(container) {
        if (!window.Vex || !window.Vex.Flow) return;
        // Clear previous
        container.innerHTML = '';

        const VF = window.Vex.Flow;
        const renderer = new VF.Renderer(container, VF.Renderer.Backends.SVG);

        renderer.resize(200, 100);
        const context = renderer.getContext();

        const notesAttr = this.getAttribute('notes') || '';
        const clefAttr = this.getAttribute('clef') || 'treble';
        const timeAttr = this.getAttribute('time') || '4/4';

        const stave = new VF.Stave(10, 0, 180);
        stave.addClef(clefAttr).addTimeSignature(timeAttr);
        stave.setContext(context).draw();

        if (notesAttr) {
            const notesList = notesAttr.split(',').map(n => n.trim()).filter(n => n);
            const notes = [];

            for (const n of notesList) {
                const parts = n.split('/');
                if (parts.length >= 2) {
                    const duration = parts.pop();
                    const keysStr = parts.join('/');
                    const keyParts = keysStr.match(/([a-zA-Z]+)(#|b)?\/?(\d+)/);
                    if (keyParts) {
                        const [, noteName, accidental, octave] = keyParts;
                        const key = `${noteName.toLowerCase()}${accidental || ''}/${octave}`;
                        const staveNote = new VF.StaveNote({ keys: [key], duration: duration, clef: clefAttr });

                        if (accidental) {
                            staveNote.addModifier(new VF.Accidental(accidental));
                        }
                        notes.push(staveNote);
                    }
                }
            }

            if (notes.length > 0) {
                const voice = new VF.Voice({ num_beats: 4, beat_value: 4 });
                voice.setStrict(false);
                voice.addTickables(notes);

                const formatter = new VF.Formatter().joinVoices([voice]).format([voice], 150);
                voice.draw(context, stave);
            }
        }

        const svg = container.querySelector("svg");
        if (svg) {
            svg.style.cssText = "height: 4em; width: auto; display: inline-block; vertical-align: middle;";
            svg.querySelectorAll("*").forEach((el) => {
                if (el.tagName !== "svg") {
                    el.style.cssText = "fill: currentColor; stroke: currentColor;";
                }
            });
        }
    }

    static get observedAttributes() {
        return ['notes', 'clef', 'time'];
    }

    attributeChangedCallback(name, oldValue, newValue) {
        if (oldValue !== newValue && this.isConnected) {
            const container = this.querySelector('.score-container') || this;
            if (window.Vex && window.Vex.Flow) {
                this.renderScore(container);
            }
        }
    }
}

if (!customElements.get('mono-score')) {
    customElements.define('mono-score', MonoScore);
}
