class MonoBrush extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.isDrawingModeActive = false;
    this.isDrawing = false;
    this.hue = 0;
    this.lastX = 0;
    this.lastY = 0;
    this.animationFrameId = null;
    this.resizeTimeout = null;
  }

  connectedCallback() {
    this.mountTemplate();
    this.setupElements();
    this.setupEventListeners();
    this.resizeCanvas();
  }

  disconnectedCallback() {
    this.removeEventListeners();
  }

  mountTemplate() {
    const template = document.getElementById("mono-brush-template");
    if (template) {
      this.shadowRoot.appendChild(template.content.cloneNode(true));
    }
  }

  setupElements() {
    this.pointer = this.shadowRoot.getElementById("pointer");
    this.canvas = this.shadowRoot.getElementById("canvas");
    this.ctx = this.canvas.getContext("2d");
  }

  setupEventListeners() {
    this.handleKeyDown = this.handleKeyDown.bind(this);
    this.handleKeyUp = this.handleKeyUp.bind(this);
    this.handleMouseMove = this.handleMouseMove.bind(this);
    this.handleMouseDown = this.handleMouseDown.bind(this);
    this.handleMouseUp = this.handleMouseUp.bind(this);
    this.handleResize = this.handleResize.bind(this);

    this.handleBlur = this.handleBlur.bind(this);

    document.addEventListener("keydown", this.handleKeyDown);
    document.addEventListener("keyup", this.handleKeyUp);
    document.addEventListener("mousemove", this.handleMouseMove, {
      passive: false,
    });

    // Canvas events for drawing
    this.canvas.addEventListener("mousedown", this.handleMouseDown);
    this.canvas.addEventListener("mousemove", this.handleMouseMove);
    this.canvas.addEventListener("mouseup", this.handleMouseUp);
    this.canvas.addEventListener("mouseout", this.handleMouseUp);

    // Touch support
    this.canvas.addEventListener(
      "touchstart",
      this.handleTouchStart.bind(this),
      { passive: false },
    );
    this.canvas.addEventListener("touchmove", this.handleTouchMove.bind(this), {
      passive: false,
    });
    this.canvas.addEventListener("touchend", this.handleMouseUp);

    window.addEventListener("resize", this.handleResize);
    window.addEventListener("blur", this.handleBlur);
  }

  removeEventListeners() {
    document.removeEventListener("keydown", this.handleKeyDown);
    document.removeEventListener("keyup", this.handleKeyUp);
    document.removeEventListener("mousemove", this.handleMouseMove);
    window.removeEventListener("resize", this.handleResize);
    window.removeEventListener("blur", this.handleBlur);
  }

  handleBlur() {
    this.isDrawingModeActive = false;
    this.updateMode();
  }

  handleResize() {
    // Debounce resize
    clearTimeout(this.resizeTimeout);
    this.resizeTimeout = setTimeout(() => {
      this.resizeCanvas();
    }, 200);
  }

  resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = window.innerHeight;
  }

  updateMode() {
    const inDrawingMode = this.isDrawingModeActive;

    // Pointer mode is disabled
    this.pointer.classList.add("hidden");

    if (inDrawingMode) {
      this.canvas.classList.add("drawing-mode");
      this.canvas.classList.remove("hidden");
    } else {
      this.canvas.classList.remove("drawing-mode");
      this.isDrawing = false;

      // Fade out and clear canvas if we were drawing
      if (!this.canvas.classList.contains("hidden")) {
        this.canvas.classList.add("hidden");
        // Wait for fade out animation before clearing
        setTimeout(() => {
          this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        }, 300);
      }
    }
  }

  handleKeyDown(e) {
    if (e.key === "CapsLock" || e.code === "CapsLock") {
      this.isDrawingModeActive = !this.isDrawingModeActive;
      this.updateMode();
    }
  }

  handleKeyUp(e) {
    // No-op for now, as drawing mode is toggled on keydown
  }

  updatePointerPosition(x, y) {
    // Pointer mode is disabled, so we don't need to update pointer position
  }

  handleMouseMove(e) {
    // Handle drawing
    if (this.isDrawing && this.isDrawingModeActive) {
      e.preventDefault(); // Prevent text selection/scrolling while drawing
      this.draw(e.clientX, e.clientY);
    }
  }

  handleMouseDown(e) {
    if (this.isDrawingModeActive) {
      this.isDrawing = true;
      this.lastX = e.clientX;
      this.lastY = e.clientY;
      this.draw(e.clientX, e.clientY); // Draw a dot
    }
  }

  handleMouseUp() {
    this.isDrawing = false;
  }

  handleTouchStart(e) {
    if (this.isDrawingModeActive) {
      e.preventDefault();
      const touch = e.touches[0];
      this.handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
    }
  }

  handleTouchMove(e) {
    if (this.isDrawing && this.isDrawingModeActive) {
      e.preventDefault();
      const touch = e.touches[0];
      this.handleMouseMove({
        clientX: touch.clientX,
        clientY: touch.clientY,
        preventDefault: () => {},
      });
    }
  }

  draw(x, y) {
    if (!this.isDrawing) return;

    this.ctx.beginPath();
    this.ctx.moveTo(this.lastX, this.lastY);
    this.ctx.lineTo(x, y);
    this.ctx.strokeStyle = `hsl(${this.hue}, 100%, 60%)`;
    this.ctx.lineWidth = 12;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
    this.ctx.stroke();

    this.lastX = x;
    this.lastY = y;
    this.hue = (this.hue + 0.1) % 360; // Slowly cycle hue
  }
}

if (!customElements.get("mono-brush")) {
  customElements.define("mono-brush", MonoBrush);
}

// Automatically inject into page
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    if (!document.querySelector("mono-brush")) {
      document.body.appendChild(document.createElement("mono-brush"));
    }
  });
} else {
  if (!document.querySelector("mono-brush")) {
    document.body.appendChild(document.createElement("mono-brush"));
  }
}
