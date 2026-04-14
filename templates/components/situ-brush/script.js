class SituBrush extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.isAltPressed = false;
    this.isShiftPressed = false;
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
    const template = document.getElementById("situ-brush-template");
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
    this.isAltPressed = false;
    this.isShiftPressed = false;
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
    const inPointerMode = this.isAltPressed && !this.isShiftPressed;
    const inDrawingMode = this.isAltPressed && this.isShiftPressed;

    if (inPointerMode) {
      this.pointer.classList.remove("hidden");
    } else {
      this.pointer.classList.add("hidden");
    }

    if (inDrawingMode) {
      this.canvas.classList.add("drawing-mode");
      this.canvas.classList.remove("hidden");
      this.pointer.classList.add("hidden"); // Hide pointer when drawing
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
    if (e.key === "Alt" || e.key === "Option") {
      this.isAltPressed = true;
      this.updateMode();
      if (this.lastMouseX !== undefined && this.lastMouseY !== undefined) {
        this.updatePointerPosition(this.lastMouseX, this.lastMouseY);
      }
    } else if (e.key === "Shift") {
      this.isShiftPressed = true;
      this.updateMode();
    }
  }

  handleKeyUp(e) {
    if (e.key === "Alt" || e.key === "Option") {
      this.isAltPressed = false;
      this.updateMode();
    } else if (e.key === "Shift") {
      this.isShiftPressed = false;
      this.updateMode();
    }
  }

  updatePointerPosition(x, y) {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }

    this.animationFrameId = requestAnimationFrame(() => {
      if (this.isAltPressed && !this.isShiftPressed) {
        this.pointer.style.left = `${x}px`;
        this.pointer.style.top = `${y}px`;
      }
    });
  }

  handleMouseMove(e) {
    // Always track the latest mouse position globally so that when Alt is pressed
    // without moving the mouse, the pointer instantly appears at the correct location.
    this.lastMouseX = e.clientX;
    this.lastMouseY = e.clientY;

    // Update pointer
    this.updatePointerPosition(e.clientX, e.clientY);

    // Handle drawing
    if (this.isDrawing && this.isAltPressed && this.isShiftPressed) {
      e.preventDefault(); // Prevent text selection/scrolling while drawing
      this.draw(e.clientX, e.clientY);
    }
  }

  handleMouseDown(e) {
    if (this.isAltPressed && this.isShiftPressed) {
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
    if (this.isAltPressed && this.isShiftPressed) {
      e.preventDefault();
      const touch = e.touches[0];
      this.handleMouseDown({ clientX: touch.clientX, clientY: touch.clientY });
    }
  }

  handleTouchMove(e) {
    if (this.isDrawing && this.isAltPressed && this.isShiftPressed) {
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

if (!customElements.get("situ-brush")) {
  customElements.define("situ-brush", SituBrush);
}

// Automatically inject into page
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    if (!document.querySelector("situ-brush")) {
      document.body.appendChild(document.createElement("situ-brush"));
    }
  });
} else {
  if (!document.querySelector("situ-brush")) {
    document.body.appendChild(document.createElement("situ-brush"));
  }
}
