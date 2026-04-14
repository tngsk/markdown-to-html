class SituGroupAssignment extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    const template = document.getElementById("situ-group-assignment-template");
    if (template) {
      this.shadowRoot.appendChild(template.content.cloneNode(true));
    }
  }

  connectedCallback() {
    this.title = this.getAttribute("title") || "グループ分け";
    const titleEl = this.shadowRoot.getElementById("group-title");
    if (titleEl) titleEl.textContent = this.title;

    this.unjoinedView = this.shadowRoot.getElementById("unjoined-view");
    this.assignedView = this.shadowRoot.getElementById("assigned-view");
    this.groupValue = this.shadowRoot.getElementById("group-value");

    this.checkAssignment();

    // セッション参加イベントをリッスンして再評価
    window.addEventListener("situ-session-changed", () => {
      this.checkAssignment();
    });
  }

  checkAssignment() {
    let sessionData = null;
    try {
      const savedSession = localStorage.getItem("situ_session_id");
      if (savedSession) {
        sessionData = JSON.parse(savedSession);
      }
    } catch (e) {}

    if (!sessionData || !sessionData.sessionId) {
      this.showUnjoined();
      return;
    }

    // 既に割り当て済みか確認
    try {
      const savedAssignment = localStorage.getItem("situ_group_assignment");
      if (savedAssignment) {
        const data = JSON.parse(savedAssignment);
        if (data.sessionId === sessionData.sessionId) {
          this.showAssigned(data.groupName);
          return;
        }
      }
    } catch (e) {}

    // まだ割り当てられていない場合は割り当てる（ランダム）
    this.assignRandomGroup(sessionData);
  }

  assignRandomGroup(sessionData) {
    const groups = [
      { id: "GROUP-A", name: "グループA" },
      { id: "GROUP-B", name: "グループB" },
      { id: "GROUP-C", name: "グループC" },
      { id: "GROUP-D", name: "グループD" }
    ];

    const assigned = groups[Math.floor(Math.random() * groups.length)];

    const payload = {
      timestamp: new Date().toISOString(),
      sessionId: sessionData.sessionId,
      userId: sessionData.userId || "unknown",
      groupId: assigned.id,
      groupName: assigned.name,
      assignmentMethod: "random"
    };

    try {
      localStorage.setItem("situ_group_assignment", JSON.stringify(payload));
    } catch(e) {
      console.info("グループ割り当ての保存に失敗しました", e);
    }

    const event = new CustomEvent("situ-data", {
      detail: payload,
      bubbles: true,
      composed: true,
    });
    this.dispatchEvent(event);

    this.showAssigned(assigned.name);
  }

  showUnjoined() {
    if(this.unjoinedView) this.unjoinedView.style.display = "block";
    if(this.assignedView) this.assignedView.style.display = "none";
  }

  showAssigned(groupName) {
    if(this.unjoinedView) this.unjoinedView.style.display = "none";
    if(this.assignedView) this.assignedView.style.display = "block";
    if(this.groupValue) this.groupValue.textContent = groupName;
  }
}

if (!customElements.get("situ-group-assignment")) {
  customElements.define("situ-group-assignment", SituGroupAssignment);
}
