/**
 * Mono Components
 *
 * Vanilla JS Web Component for code blocks.
 * Implements "Light DOM" enhancement strategy: Wraps the original Markdown
 * <pre><code> output to preserve SEO and accessibility, while injecting
 * a copy button and syntax highlighting functionality.
 */

class MonoCodeBlock extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    // Component state
    this.language = this.getAttribute("language") || "";
    this.refs = {};
  }

  connectedCallback() {
    this.mountTemplate();
    this.setupEventListeners();
    this.initializeSyntaxHighlighting();
  }

  mountTemplate() {
    const template = document.getElementById("mono-code-block-template");
    if (!template) {
      console.error("Template #mono-code-block-template not found.");
      return;
    }
    this.shadowRoot.appendChild(template.content.cloneNode(true));

    // Cache references
    this.shadowRoot.querySelectorAll("[data-ref]").forEach((el) => {
      this.refs[el.dataset.ref] = el;
    });

    // Set Header Label
    if (this.refs.languageLabel) {
      this.refs.languageLabel.textContent = this.language
        ? this.language
        : "Code";
    }

    // Move Light DOM content (the original <pre><code> from markdown) into the slot container
    if (this.refs.contentSlot) {
      // Create a <slot> to project the light DOM content into the Shadow DOM
      const slot = document.createElement("slot");
      this.refs.contentSlot.appendChild(slot);
    }
  }

  setupEventListeners() {
    if (this.refs.copyButton) {
      this.refs.copyButton.addEventListener("click", () =>
        this.handleCopyClick(),
      );
    }
  }

  handleCopyClick() {
    // Look for the <code> element within the Light DOM (children of <mono-code-block>)
    const codeElement = this.querySelector("code");
    if (!codeElement) return;

    // Use textContent to grab raw text, avoiding HTML tags from highlight.js
    const text = codeElement.textContent;

    navigator.clipboard
      .writeText(text)
      .then(() => {
        this.showCopySuccess();
      })
      .catch((err) => {
        console.error("Failed to copy text: ", err);
        this.showCopyError();
      });
  }

  showCopySuccess() {
    const btn = this.refs.copyButton;
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.innerHTML = "✅ Copied!";
    btn.classList.add("copied");

    // Reset after 2 seconds
    setTimeout(() => {
      btn.innerHTML = originalText;
      btn.classList.remove("copied");
    }, 2000);
  }

  showCopyError() {
    const btn = this.refs.copyButton;
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.innerHTML = "❌ Error";

    setTimeout(() => {
      btn.innerHTML = originalText;
    }, 2000);
  }

  initializeSyntaxHighlighting() {
    // If highlight.js is loaded globally, apply it to the Light DOM <code> element
    if (window.hljs) {
      const codeElement = this.querySelector("code");
      if (codeElement) {
        // Ensure the language class is set for hljs
        if (
          this.language &&
          !codeElement.classList.contains(`language-${this.language}`)
        ) {
          codeElement.classList.add(`language-${this.language}`);
        }
        window.hljs.highlightElement(codeElement);
      }
    }
  }
}

// Register the custom element
if (!customElements.get("mono-code-block")) {
  customElements.define("mono-code-block", MonoCodeBlock);
}
