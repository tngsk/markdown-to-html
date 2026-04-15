document.addEventListener('DOMContentLoaded', () => {
    const storeEl = document.getElementById('mono-asset-store');
    if (storeEl) {
        try {
            const assets = JSON.parse(storeEl.innerHTML);
            const elements = document.querySelectorAll('[data-lazy-src], [data-lazy-src-a], [data-lazy-src-b]');
            elements.forEach(el => {
                const src = el.getAttribute('data-lazy-src');
                if (src && assets[src]) {
                    el.setAttribute('src', assets[src]);
                    el.removeAttribute('data-lazy-src');
                }

                const srcA = el.getAttribute('data-lazy-src-a');
                if (srcA && assets[srcA]) {
                    el.setAttribute('src-a', assets[srcA]);
                    el.removeAttribute('data-lazy-src-a');
                }

                const srcB = el.getAttribute('data-lazy-src-b');
                if (srcB && assets[srcB]) {
                    el.setAttribute('src-b', assets[srcB]);
                    el.removeAttribute('data-lazy-src-b');
                }
            });
        } catch (e) {
            console.error('Failed to load lazy assets', e);
        }
    }
});