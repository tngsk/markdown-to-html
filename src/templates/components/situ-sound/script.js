class SituSound extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    const template = document.getElementById("situ-sound-template");
    if (template) {
      this.shadowRoot.appendChild(template.content.cloneNode(true));
    }

    this.audio = this.shadowRoot.querySelector(".situ-sound-audio");
    this.playBtn = this.shadowRoot.querySelector(".situ-sound-play-btn");
    this.labelEl = this.shadowRoot.querySelector(".situ-sound-label");
    this.iconPlay = this.shadowRoot.querySelector(".situ-sound-icon-play");
    this.iconPause = this.shadowRoot.querySelector(".situ-sound-icon-pause");

    this.isPlaying = false;
  }

  connectedCallback() {
    const label = this.getAttribute("label");
    if (label && this.labelEl) {
      this.labelEl.textContent = label;
    }

    const rawSrc = this.getAttribute("src");
    if (rawSrc && this.audio) {
      // Handle asset-store logic
      if (rawSrc.startsWith("asset-")) {
        const store = document.getElementById("situ-asset-store");
        if (store) {
          try {
            const assets = JSON.parse(store.innerHTML);
            if (assets[rawSrc]) {
              this.audio.src = assets[rawSrc];
            }
          } catch (e) {
            console.error("Asset store parse error in situ-sound:", e);
          }
        }
      } else {
        this.audio.src = rawSrc;
      }
    }

    if (this.playBtn && this.audio) {
      this.playBtn.addEventListener("click", () => this.togglePlay());
      this.audio.addEventListener("ended", () => this.onEnded());
      this.audio.addEventListener("pause", () => this.onPause());
      this.audio.addEventListener("play", () => this.onPlay());
    }
  }

  togglePlay() {
    if (this.audio.paused) {
      this.audio.play().catch(e => console.error("Audio playback failed:", e));
    } else {
      this.audio.pause();
    }
  }

  onPlay() {
    this.isPlaying = true;
    if (this.iconPlay) this.iconPlay.style.display = "none";
    if (this.iconPause) this.iconPause.style.display = "block";
  }

  onPause() {
    this.isPlaying = false;
    if (this.iconPlay) this.iconPlay.style.display = "block";
    if (this.iconPause) this.iconPause.style.display = "none";
  }

  onEnded() {
    this.onPause();
    this.audio.currentTime = 0;
  }
}

customElements.define("situ-sound", SituSound);
