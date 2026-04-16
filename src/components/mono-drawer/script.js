class MonoDrawer extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    const template = document.getElementById('mono-drawer-template');
    if (template) {
        this.shadowRoot.appendChild(template.content.cloneNode(true));
    } else {
        console.error('mono-drawer-template not found');
        return;
    }

    const container = this.shadowRoot.getElementById('drawer-container');
    const handle = this.shadowRoot.getElementById('drawer-handle');
    const handleLabel = this.shadowRoot.getElementById('handle-label');

    const label = this.getAttribute('label') || 'Drawer';
    const position = this.getAttribute('position') || 'left';
    const isOpen = this.hasAttribute('open') && this.getAttribute('open') !== 'false';

    // The backend already escapes the HTML attributes during parsing,
    // so we can safely use innerHTML to support basic formatting/icons if they were allowed,
    // but to be absolutely safe against DOM XSS, we use textContent.
    handleLabel.textContent = label;

    container.classList.add(position);
    if (isOpen) {
      container.classList.add('open');
    }

    handle.addEventListener('click', () => {
      container.classList.toggle('open');
    });
  }
}

if (!customElements.get('mono-drawer')) {
    customElements.define('mono-drawer', MonoDrawer);
}
