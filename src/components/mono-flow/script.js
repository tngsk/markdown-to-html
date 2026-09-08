const MonoFlowGeometry = (() => {
  function calculateFlowCurve(fromRect, toRect, wrapperRect, direction = "LR") {
    // Calculate center points relative to the wrapper
    const fromX = fromRect.left - wrapperRect.left + fromRect.width / 2;
    const fromY = fromRect.top - wrapperRect.top + fromRect.height / 2;

    const toX = toRect.left - wrapperRect.left + toRect.width / 2;
    const toY = toRect.top - wrapperRect.top + toRect.height / 2;

    let startX, startY, endX, endY, d;
    const curvature = 0.5;

    if (direction === "TB") {
      // Vertical layout: from bottom center to top center
      startX = fromX;
      startY = fromY + fromRect.height / 2;
      endX = toX;
      endY = toY - toRect.height / 2;

      const dy = endY - startY;
      const control1X = startX;
      const control1Y = startY + dy * curvature;
      const control2X = endX;
      const control2Y = endY - dy * curvature;

      d = `M ${startX} ${startY} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${endX} ${endY}`;
    } else {
      // Horizontal layout: from right center to left center
      startX = fromX + fromRect.width / 2;
      startY = fromY;
      endX = toX - toRect.width / 2;
      endY = toY;

      const dx = endX - startX;
      const control1X = startX + dx * curvature;
      const control1Y = startY;
      const control2X = endX - dx * curvature;
      const control2Y = endY;

      d = `M ${startX} ${startY} C ${control1X} ${control1Y}, ${control2X} ${control2Y}, ${endX} ${endY}`;
    }

    const midX = startX + (endX - startX) / 2;
    const midY = startY + (endY - startY) / 2;

    return {
      startX,
      startY,
      endX,
      endY,
      d,
      midX,
      midY,
    };
  }

  return { calculateFlowCurve };
})();

if (typeof module !== "undefined" && module.exports) {
  module.exports = MonoFlowGeometry;
}

if (typeof MonoBaseElement === "undefined") {
  var MonoBaseElement = typeof HTMLElement !== "undefined" ? HTMLElement : class {};
}

class MonoFlow extends MonoBaseElement {
  constructor() {
    super();
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
        this.mountTemplate('template-mono-flow');

    // Handle title
    const title = this.getAttribute("title");
    if (title) {
      const titleEl = this.shadowRoot.getElementById("title");
      if (titleEl) {
        titleEl.textContent = title;
        titleEl.style.display = "block";
      }
    }

    // Process nodes and edges after the slot has been populated
    // Use setTimeout to ensure the light DOM is fully rendered and layout is calculated
    setTimeout(() => {
      this.initGraph();
    }, 0);
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
    svg.textContent = "";

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
      "var(--color-primary, #3b82f6)";
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

      const direction = this.getAttribute("direction") || "LR";
      const geom = MonoFlowGeometry.calculateFlowCurve(
        fromRect,
        toRect,
        wrapperRect,
        direction
      );

      const pathEl = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "path",
      );
      pathEl.setAttribute("d", geom.d);
      pathEl.setAttribute("class", "flow-path");
      pathEl.setAttribute("marker-end", "url(#arrow)");
      svg.appendChild(pathEl);

      // Add label if it exists
      if (edge.label) {
        const groupEl = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "g",
        );

        const textEl = document.createElementNS(
          "http://www.w3.org/2000/svg",
          "text",
        );
        textEl.setAttribute("x", geom.midX);
        textEl.setAttribute("y", geom.midY);
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

if (typeof customElements !== "undefined") {
  customElements.define("mono-flow", MonoFlow);
}
