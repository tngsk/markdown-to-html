document.addEventListener('DOMContentLoaded', () => {
    const storeEl = document.getElementById('mono-asset-store');

    const isValidUrl = (url) => {
        if (!url || typeof url !== 'string') return false;
        try {
            const parsed = new URL(url, window.location.href);
            const protocol = parsed.protocol.toLowerCase();
            return ['http:', 'https:', 'data:'].includes(protocol);
        } catch (e) {
            // If URL parsing fails, it might be a relative path which is fine,
            // but to be safe against complex protocol bypasses, we ensure it doesn't contain forbidden protocols
            // Actually, `new URL(url, window.location.href)` handles relative URLs perfectly.
            // If it still throws, it's malformed.
            return false;
        }
    };

    if (storeEl) {
        try {
            const assets = JSON.parse(storeEl.content ? storeEl.content.textContent : storeEl.textContent);
            const elements = document.querySelectorAll('[data-lazy-src], [data-lazy-src-a], [data-lazy-src-b]');
            elements.forEach(el => {
                const src = el.getAttribute('data-lazy-src');
                if (src && assets[src] && isValidUrl(assets[src])) {
                    el.setAttribute('src', assets[src]);
                    el.removeAttribute('data-lazy-src');
                }

                const srcA = el.getAttribute('data-lazy-src-a');
                if (srcA && assets[srcA] && isValidUrl(assets[srcA])) {
                    el.setAttribute('src-a', assets[srcA]);
                    el.removeAttribute('data-lazy-src-a');
                }

                const srcB = el.getAttribute('data-lazy-src-b');
                if (srcB && assets[srcB] && isValidUrl(assets[srcB])) {
                    el.setAttribute('src-b', assets[srcB]);
                    el.removeAttribute('data-lazy-src-b');
                }
            });
        } catch (e) {
            console.error('Failed to load lazy assets', e);
        }
    }
});