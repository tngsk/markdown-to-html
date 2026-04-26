import os
import pytest
from playwright.sync_api import sync_playwright

def test_mono_score_width_bounds():
    """
    Test that the last note in a mono-score component does not overflow
    its SVG bounding box (renderer width).
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js"></script>
        <script>
        class MonoScore extends HTMLElement {
            constructor() {
                super();
            }

            async connectedCallback() {
                const container = this;

                // Ensure VexFlow is loaded
                await this.loadVexFlow();

                this.renderScore(container);
            }

            async loadVexFlow() {
                if (window.Vex && window.Vex.Flow) return;

                if (!window.__vexFlowLoadingPromise) {
                    window.__vexFlowLoadingPromise = new Promise((resolve, reject) => {
                        const script = document.createElement('script');
                        script.src = "https://cdn.jsdelivr.net/npm/vexflow@4.2.2/build/cjs/vexflow.js";
                        script.onload = () => {
                            if (window.Vex && window.Vex.Flow) resolve();
                        };
                        script.onerror = reject;
                        document.head.appendChild(script);
                    });
                }
                return window.__vexFlowLoadingPromise;
            }

            renderScore(container) {
                if (!window.Vex || !window.Vex.Flow) return;
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
                    const rawTokens = notesAttr.split(/[\\s,]+/).filter(n => n);
                    const notes = [];

                    for (const token of rawTokens) {
                        const keyParts = token.match(/([a-zA-Z]+)(#|b)?\\/?(\\d+)?/);
                        if (keyParts) {
                            const [, noteName, accidental, octave] = keyParts;
                            const key = `${noteName.toLowerCase()}${accidental || ''}/${octave || '4'}`;
                            const staveNote = new VF.StaveNote({ keys: [key], duration: 'q', clef: clefAttr });
                            notes.push(staveNote);
                        }
                    }

                    if (notes.length > 0) {
                        const staveWidth = Math.max(150, notes.length * 40);
                        const rendererWidth = staveWidth + stave.getX() + 20;
                        renderer.resize(rendererWidth, 120);
                        stave.setWidth(staveWidth).draw();

                        const voice = new VF.Voice({ num_beats: notes.length, beat_value: 4 });
                        voice.setStrict(false);
                        voice.addTickables(notes);

                        const formatter = new VF.Formatter().joinVoices([voice]).format([voice], staveWidth - (stave.getNoteStartX() - stave.getX()) - 10);
                        voice.draw(context, stave);

                        // Expose test attributes
                        const lastNote = notes[notes.length - 1];
                        const bbox = lastNote.getBoundingBox();
                        this.setAttribute('data-last-x', bbox.getX() + bbox.getW());
                        this.setAttribute('data-renderer-width', rendererWidth);
                    } else {
                        stave.draw();
                    }
                } else {
                    stave.draw();
                }
            }
        }
        if (!customElements.get('mono-score')) {
            customElements.define('mono-score', MonoScore);
        }
        </script>
    </head>
    <body>
        <mono-score notes="C4 D4 E4 F4 G4 A4 B4 C5"></mono-score>
    </body>
    </html>
    """

    test_file = "test_score_render.html"
    with open(test_file, 'w') as f:
        f.write(html_content)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto('file://' + os.path.abspath(test_file))

            # Wait for component to render and set attributes
            page.wait_for_selector('mono-score[data-last-x]')

            last_x = float(page.evaluate("document.querySelector('mono-score').getAttribute('data-last-x')"))
            renderer_width = float(page.evaluate("document.querySelector('mono-score').getAttribute('data-renderer-width')"))

            # The last note's right edge should be less than the renderer width
            assert last_x <= renderer_width, f"Note overflows: {last_x} > {renderer_width}"

            browser.close()
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
