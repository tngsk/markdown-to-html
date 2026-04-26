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
        stave.setContext(context);

        if (notesAttr) {
            const rawTokens = notesAttr.split(/[\s,]+/).filter(n => n);
            const notes = [];

            for (const token of rawTokens) {
                if (token === '|') {
                    notes.push(new VF.BarNote());
                    continue;
                }

                if (/^\d+$/.test(token) || /^[whq8]$/.test(token)) {
                    if (notes.length > 0) {
                        const prev = notes[notes.length - 1];
                        if (prev instanceof VF.StaveNote) {
                            let dur = token;
                            if (token === '2') dur = 'h';
                            else if (token === '4') dur = 'q';
                            else if (token === '1') dur = 'w';
                            else if (token === '8') dur = '8';

                            const newNote = new VF.StaveNote({
                                keys: prev.keys,
                                duration: dur,
                                clef: prev.clef
                            });
                            const keyParts = prev.keys[0].match(/([a-zA-Z]+)(#|b)?\/?(\d+)/);
                            if (keyParts && keyParts[2]) {
                                newNote.addModifier(new VF.Accidental(keyParts[2]));
                            }
                            notes[notes.length - 1] = newNote;
                        }
                    }
                    continue;
                }

                let keysStr = token;
                let duration = 'q';

                if (token.includes('/')) {
                    const parts = token.split('/');
                    const lastPart = parts[parts.length - 1];
                    if (['w', 'h', 'q', '8', '16', '32'].includes(lastPart)) {
                        duration = parts.pop();
                    }
                    keysStr = parts.join('/');
                }

                const keyParts = keysStr.match(/([a-zA-Z]+)(#|b)?\/?(\d+)?/);
                if (keyParts) {
                    const [, noteName, accidental, octave] = keyParts;
                    const key = `${noteName.toLowerCase()}${accidental || ''}/${octave || '4'}`;
                    const staveNote = new VF.StaveNote({ keys: [key], duration: duration, clef: clefAttr });

                    if (accidental) {
                        staveNote.addModifier(new VF.Accidental(accidental));
                    }
                    notes.push(staveNote);
                }
            }

            if (notes.length > 0) {
                // Determine bounding box based on number of notes to avoid crowding
                const staveWidth = Math.max(150, notes.length * 40);
                const rendererWidth = staveWidth + stave.getX() + 20;
                renderer.resize(rendererWidth, 120);
                stave.setWidth(staveWidth).draw();

                // Calculate total ticks/beats to configure the voice correctly
                let totalTicks = 0;
                notes.forEach(n => {
                    if (n instanceof VF.StaveNote) {
                        totalTicks += n.getTicks().value();
                    }
                });

                // Usually 4096 ticks per beat in VexFlow, so we calculate total beats
                const BEAT_RESOLUTION = 4096;
                const totalBeats = Math.ceil(totalTicks / BEAT_RESOLUTION) || 4;

                const voice = new VF.Voice({ num_beats: totalBeats, beat_value: 4 });
                voice.setStrict(false);
                voice.addTickables(notes);

                const formatter = new VF.Formatter().joinVoices([voice]).format([voice], staveWidth - (stave.getNoteStartX() - stave.getX()) - 10);
                voice.draw(context, stave);
            } else {
                stave.draw();
            }
        } else {
            stave.draw();
        }

        const svg = container.querySelector("svg");
        if (svg) {
            svg.style.cssText = "height: 6em; width: auto; display: inline-block; vertical-align: middle;";
            svg.querySelectorAll("*").forEach((el) => {
                if (el.tagName !== "svg") {
                    if (el.getAttribute("fill") === "black" || el.getAttribute("fill") === "#000000") {
                        el.setAttribute("fill", "currentColor");
                    }
                    if (el.getAttribute("stroke") === "black" || el.getAttribute("stroke") === "#000000") {
                        el.setAttribute("stroke", "currentColor");
                    }
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
