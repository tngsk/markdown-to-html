/**
 * Interactive-MD Components
 *
 * Vanilla JS Web Components for educational and research acoustic systems.
 * Designed with a clean, readable aesthetic (themes like Lab-Gear can be applied externally).
 */

class SituPoll extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });

    // Component state
    this.title = this.getAttribute("title") || "Poll";
    this.options = (this.getAttribute("options") || "")
      .split(",")
      .map((opt) => opt.trim())
      .filter((opt) => opt);
    this.componentId =
      this.getAttribute("id") ||
      `poll-${Math.random().toString(36).substring(2, 9)}`;
    this.hasVoted = false;

    // Load state from mock storage
    this.checkPreviousVote();
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  checkPreviousVote() {
    try {
      const savedData = localStorage.getItem(`situ_poll_${this.componentId}`);
      if (savedData) {
        const data = JSON.parse(savedData);
        this.hasVoted = true;
        this.selectedValue = data.selected;
      }
    } catch (e) {
      console.warn("Failed to read from localStorage:", e);
    }
  }

  saveVote(value) {
    const payload = {
      componentId: this.componentId,
      type: "poll",
      title: this.title,
      selected: value,
      timestamp: new Date().toISOString(),
    };

    // Phase 3 Compatibility: Dispatch custom event for future backend integration
    const event = new CustomEvent("situ:vote", {
      detail: payload,
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);

    // Mock Persistence (Phase 2)
    try {
      localStorage.setItem(
        `situ_poll_${this.componentId}`,
        JSON.stringify(payload),
      );
      this.hasVoted = true;
      this.selectedValue = value;
      this.render(); // Re-render to show voted state
    } catch (e) {
      console.error("Failed to save vote:", e);
      alert("投票の保存に失敗しました。");
    }
  }

  render() {
    // Clean, readable styling matching the project's default aesthetic
    const style = `
            :host {
                display: block;
                margin: 1.5rem 0;
                font-family: var(--situ-font-family, system-ui, -apple-system, sans-serif);
                color: var(--situ-text-color, #333);
                background: var(--situ-bg-color, #f9f9f9);
                border: 1px solid var(--situ-border-color, #e0e0e0);
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                max-width: 600px;
            }

            .poll-header {
                margin-top: 0;
                margin-bottom: 1rem;
                font-size: 1.1rem;
                font-weight: 600;
                line-height: 1.4;
            }

            .options-container {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .option-label {
                display: flex;
                align-items: center;
                padding: 0.75rem 1rem;
                border: 1px solid var(--situ-border-color, #d1d5db);
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: background-color 0.15s ease, border-color 0.15s ease;
            }

            .option-label:hover:not(.voted) {
                background: var(--situ-hover-bg, #f3f4f6);
            }

            .option-label.selected {
                border-color: var(--situ-primary-color, #3b82f6);
                background: var(--situ-primary-light, #eff6ff);
            }

            input[type="radio"] {
                margin-right: 1rem;
                transform: scale(1.2);
                cursor: pointer;
            }

            button.submit-btn {
                margin-top: 1.5rem;
                padding: 0.5rem 1.5rem;
                background-color: var(--situ-primary-color, #3b82f6);
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 1rem;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s ease;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }

            button.submit-btn:hover:not(:disabled) {
                background-color: var(--situ-primary-dark, #2563eb);
            }

            button.submit-btn:disabled {
                background-color: var(--situ-disabled-color, #9ca3af);
                cursor: not-allowed;
            }

            .voted-message {
                margin-top: 1rem;
                font-size: 0.9rem;
                color: var(--situ-success-color, #059669);
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }

            /* Read-only state for already voted */
            .option-label.voted {
                cursor: default;
                opacity: 0.8;
            }
        `;

    const optionsHtml = this.options
      .map((opt, index) => {
        const isSelected = this.hasVoted && this.selectedValue === opt;
        const disabledAttr = this.hasVoted ? "disabled" : "";
        const checkedAttr = isSelected ? "checked" : "";
        const classNames = `option-label ${isSelected ? "selected" : ""} ${this.hasVoted ? "voted" : ""}`;

        return `
                <label class="${classNames}">
                    <input type="radio" name="poll-option" value="${opt}" ${checkedAttr} ${disabledAttr}>
                    <span class="option-text">${opt}</span>
                </label>
            `;
      })
      .join("");

    const submitHtml = this.hasVoted
      ? `<div class="voted-message">
                 <svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M10.97 4.97a.75.75 0 0 1 1.07 1.05l-3.99 4.99a.75.75 0 0 1-1.08.02L4.324 8.384a.75.75 0 1 1 1.06-1.06l2.094 2.093 3.473-4.425a.267.267 0 0 1 .02-.022z"/></svg>
                 記録されました
               </div>`
      : `<button class="submit-btn" id="submitBtn" disabled>記録する</button>`;

    this.shadowRoot.innerHTML = `
            <style>${style}</style>
            <div class="poll-wrapper">
                <h3 class="poll-header">${this.title}</h3>
                <div class="options-container">
                    ${optionsHtml}
                </div>
                ${submitHtml}
            </div>
        `;
  }

  setupEventListeners() {
    if (this.hasVoted) return;

    const radios = this.shadowRoot.querySelectorAll('input[type="radio"]');
    const submitBtn = this.shadowRoot.getElementById("submitBtn");

    // Enable submit button only when an option is selected
    radios.forEach((radio) => {
      radio.addEventListener("change", () => {
        if (submitBtn) {
          submitBtn.disabled = false;
        }

        // Visual feedback for selection
        this.shadowRoot
          .querySelectorAll(".option-label")
          .forEach((label) => label.classList.remove("selected"));
        radio.closest(".option-label").classList.add("selected");
      });
    });

    if (submitBtn) {
      submitBtn.addEventListener("click", () => {
        const selectedRadio = this.shadowRoot.querySelector(
          'input[type="radio"]:checked',
        );
        if (selectedRadio) {
          this.saveVote(selectedRadio.value);
        }
      });
    }
  }
}

// Register the custom element
if (!customElements.get("situ-poll")) {
  customElements.define("situ-poll", SituPoll);
}
