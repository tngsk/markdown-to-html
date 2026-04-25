class MonoFlow extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this.edges = [];
    this.nodes = new Map(); // id -> element
    this.resizeObserver = null;
  }

  connectedCallback() {
    this.render();
  }

  disconnectedCallback() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    window.removeEventListener("resize", this.drawEdgesBound);
  }

  render() {
    const template = document.getElementById("template-mono-flow");
    if (!template) {
      console.error("Template for mono-flow not found.");
      return;
    }
    this.shadowRoot.appendChild(template.content.cloneNode(true));

    // Handle title
    const title = this.getAttribute("title");
    if (title) {
      const titleEl = this.shadowRoot.getElementById("title");
      if (titleEl) {
        titleEl.textContent = title;
        titleEl.style.display = "block";
      }
    }

    // Inject styles for light DOM elements since ::slotted only works for top-level
    this.injectLightDOMStyles();

    // Process nodes and edges after the slot has been populated
    // Use setTimeout to ensure the light DOM is fully rendered and layout is calculated
    setTimeout(() => {
      this.initGraph();
    }, 0);
  }

  injectLightDOMStyles() {
    // Only inject once per document to avoid style duplication
    if (document.getElementById("mono-flow-light-styles")) return;

    const style = document.createElement("style");
    style.id = "mono-flow-light-styles";
    style.textContent = `
      mono-flow .flow-container {
        display: flex;
        flex-direction: row;
        align-items: stretch;
        gap: var(--flow-gap-x, 3rem);
        position: relative;
        z-index: 2;
        width: 100%;
      }
      mono-flow .flow-layer {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        gap: var(--flow-gap-y, 1.5rem);
        flex: 1;
        min-width: 0;
        z-index: 2;
      }
      mono-flow .flow-node {
        background-color: var(--flow-node-bg, #ffffff);
        border: var(--flow-node-border-width, 2px) solid var(--flow-node-border, #d1d5db);
        border-radius: var(--flow-node-radius, 0.25rem);
        padding: var(--flow-node-padding, 0.75rem 1.25rem);
        width: 100%;
        box-sizing: border-box;
        color: var(--flow-text-color, #374151);
        font-size: 0.75rem;
        font-weight: 500;
        text-align: center;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease-in-out;
        cursor: default;
        user-select: none;
        z-index: 2;
      }
      mono-flow .flow-node:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-color: var(--flow-line-color, #4f46e5);
      }
    `;
    document.head.appendChild(style);
  }

  initGraph() {
    // Find the JSON script tag in the light DOM
    const scriptEl = this.querySelector("script.flow-connections");
    if (scriptEl) {
      try {
        this.edges = JSON.parse(scriptEl.textContent);
      } catch (e) {
        console.error("Failed to parse mono-flow edges JSON:", e);
      }
    }

    // Collect all nodes
    const nodeEls = this.querySelectorAll(".flow-node");
    nodeEls.forEach((el) => {
      const id = el.getAttribute("data-id");
      if (id) {
        this.nodes.set(id, el);
      }
    });

    this.drawEdgesBound = this.drawEdges.bind(this);

    // Initial draw
    this.drawEdges();

    // Redraw on resize
    window.addEventListener("resize", this.drawEdgesBound);

    // Also observe the wrapper for size changes (e.g., if a parent container changes size)
    const wrapper = this.shadowRoot.querySelector(".flow-content-wrapper");
    if (wrapper && window.ResizeObserver) {
      this.resizeObserver = new ResizeObserver(() => {
        this.drawEdges();
      });
      this.resizeObserver.observe(wrapper);
    }
  }

  drawEdges() {
    const svg = this.shadowRoot.querySelector(".flow-svg-overlay");
    const wrapper = this.shadowRoot.querySelector(".flow-content-wrapper");
    if (!svg || !wrapper) return;

    // Clear existing SVGs
    svg.innerHTML = "";

    // Calculate wrapper bounds to make absolute coordinates relative to the wrapper
    const wrapperRect = wrapper.getBoundingClientRect();

    // Define marker for arrowheads
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    const marker = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "marker",
    );
    marker.setAttribute("id", "arrow");
    marker.setAttribute("viewBox", "0 0 10 10");
    marker.setAttribute("refX", "8");
    marker.setAttribute("refY", "5");
    marker.setAttribute("markerWidth", "6");
    marker.setAttribute("markerHeight", "6");
    marker.setAttribute("orient", "auto-start-reverse");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", "M 0 0 L 10 5 L 0 10 z");
    // Read the line color variable from the host
    const lineColor =
      getComputedStyle(this).getPropertyValue("--flow-line-color").trim() ||
      "#4f46e5";
    path.setAttribute("fill", lineColor);

    marker.appendChild(path);
    defs.appendChild(marker);
    svg.appendChild(defs);

    this.edges.forEach((edge) => {
      const fromEl = this.nodes.get(edge.from);
      const toEl = this.nodes.get(edge.to);

      if (!fromEl || !toEl) return;

      const fromRect = fromEl.getBoundingClientRect();
      const toRect = toEl.getBoundingClientRect();

      // Calculate center points relative to the wrapper
      const fromX = fromRect.left - wrapperRect.left + fromRect.width / 2;
      const fromY = fromRect.top - wrapperRect.top + fromRect.height / 2;

      const toX = toRect.left - wrapperRect.left + toRect.width / 2;
      const toY = toRect.top - wrapperRect.top + toRect.height / 2;

      // Determine connection points based on layout direction (LR by default)
      // For horizontal layout: from right center to left center
      const startX = fromX + fromRect.width / 2;
      const startY = fromY;

      const endX = toX - toRect.width / 2;
      const endY = toY;

      // Create an S-curve path
      const curvature = 0.5; // adjust for sharper or softer curves
      const dx = endX - startX;
      // const dy = endY - startY; // Not strictly needed for cubic bezier logic here
      const control1X = startX + dx * curvature;
      const control1Y = startY;
      const control2X = endX - dx * curvature;
      const control2Y = endY;

      const d = `M ${startX} ${startY} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${endX} ${endY}`;

      const pathEl = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "path",
      );
      pathEl.setAttribute("d", d);
      pathEl.setAttribute("class", "flow-path");
      pathEl.setAttribute("marker-end", "url(#arrow)");
      svg.appendChild(pathEl);

      // Add label if it exists
      if (edge.label) {
        // Calculate the midpoint of the bezier curve for the label
        // A simple approximation is the exact midpoint of start and end
        const midX = startX + (endX - startX) / 2;
        const midY = startY + (endY - startY) / 2;

        const groupEl = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "g",
        );

        const textEl = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "text",
        );
        textEl.setAttribute("x", midX);
        textEl.setAttribute("y", midY);
        textEl.setAttribute("class", "flow-label");
        textEl.textContent = edge.label;

        // Create a background rect for the text
        const rectEl = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "rect",
        );
        rectEl.setAttribute("class", "flow-label-bg");

        groupEl.appendChild(rectEl);
        groupEl.appendChild(textEl);
        svg.appendChild(groupEl);

        // We need to wait for text to render to get its bounding box to size the rect
        // Use a tiny timeout or requestAnimationFrame
        requestAnimationFrame(() => {
          try {
            const bbox = textEl.getBBox();
            const padding = 4;
            rectEl.setAttribute("x", bbox.x - padding);
            rectEl.setAttribute("y", bbox.y - padding);
            rectEl.setAttribute("width", bbox.width + padding * 2);
            rectEl.setAttribute("height", bbox.height + padding * 2);
          } catch (e) {
            // getBBox might fail if the SVG is not fully visible/rendered
          }
        });
      }
    });
  }
}

customElements.define("mono-flow", MonoFlow);
