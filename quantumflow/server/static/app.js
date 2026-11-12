/**
 * QuantumFlow Multiverse Visualization Engine
 * Connects to the SSE event stream, draws real-time branching topology on HTML5 Canvas,
 * and maintains reactive UI metrics.
 */

(() => {
  const state = {
    rootState: {},
    timelines: {},
    metrics: { superposed: 0, collapsed: 0, decohered: 0, fingerprint: "000000000000" },
    events: [],
    canvasNodes: []
  };

  const canvas = document.getElementById("topologyCanvas");
  const ctx = canvas.getContext("2d");
  let width = (canvas.width = canvas.parentElement.clientWidth);
  let height = (canvas.height = canvas.parentElement.clientHeight);

  window.addEventListener("resize", () => {
    width = canvas.width = canvas.parentElement.clientWidth;
    height = canvas.height = canvas.parentElement.clientHeight;
  });

  // Colors
  const COLORS = {
    ROOT: "#ffffff",
    SUPERPOSED: "#00f3ff",
    COLLAPSED: "#00ff9d",
    DECOHERENT: "#ff3366",
    DISSOLVED: "#4a5568",
    BG_LINE: "rgba(0, 243, 255, 0.2)"
  };

  // Node layout builder
  function updateLayout() {
    const list = Object.values(state.timelines);
    const nodes = [];

    // Root node at the left center
    const rootNode = {
      id: "root",
      name: "ROOT REALITY",
      status: "ROOT",
      x: 100,
      y: height / 2,
      radius: 12,
      color: COLORS.ROOT
    };
    nodes.push(rootNode);

    // Filter to last 12 timelines to avoid clutter
    const recent = list.slice(-12);
    const count = recent.length;

    recent.forEach((tl, idx) => {
      // Fan out in an arc or branching layers
      const angleStep = Math.PI / (Math.max(count, 1) + 1);
      const angle = -Math.PI / 2 + angleStep * (idx + 1);
      const dist = Math.min(width * 0.42, 320);

      const x = rootNode.x + Math.cos(angle * 0.7) * dist + 80;
      const y = rootNode.y + Math.sin(angle * 0.7) * (height * 0.38);

      let color = COLORS.SUPERPOSED;
      let radius = 8;
      if (tl.status === "COLLAPSED") {
        color = COLORS.COLLAPSED;
        radius = 11;
      } else if (tl.status === "DECOHERENT") {
        color = COLORS.DECOHERENT;
        radius = 7;
      } else if (tl.status === "DISSOLVED") {
        color = COLORS.DISSOLVED;
        radius = 6;
      }

      nodes.push({
        id: tl.id,
        name: tl.name,
        status: tl.status,
        x,
        y,
        radius,
        color,
        latency: tl.latencyMs,
        entropy: tl.entropy,
        parentId: "root"
      });
    });

    state.canvasNodes = nodes;
  }

  // Animation Loop
  let pulseTick = 0;
  function render() {
    pulseTick += 0.04;
    ctx.clearRect(0, 0, width, height);

    // Draw Quantum grid background particles
    ctx.fillStyle = "rgba(0, 243, 255, 0.03)";
    for (let i = 0; i < 30; i++) {
      const px = (Math.sin(pulseTick * 0.3 + i * 2) * 0.5 + 0.5) * width;
      const py = (Math.cos(pulseTick * 0.2 + i * 3) * 0.5 + 0.5) * height;
      ctx.beginPath();
      ctx.arc(px, py, 1.5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Draw Connections between root and child nodes
    const root = state.canvasNodes.find(n => n.id === "root");
    if (root) {
      state.canvasNodes.forEach(node => {
        if (node.id === "root") return;

        ctx.beginPath();
        ctx.moveTo(root.x, root.y);

        // Bezier curve connection
        const cx = (root.x + node.x) / 2;
        const cy = node.y;
        ctx.quadraticCurveTo(cx, cy, node.x, node.y);

        if (node.status === "COLLAPSED") {
          ctx.strokeStyle = "rgba(0, 255, 157, 0.7)";
          ctx.lineWidth = 3;
        } else if (node.status === "SUPERPOSED") {
          ctx.strokeStyle = `rgba(0, 243, 255, ${0.4 + Math.sin(pulseTick * 3) * 0.2})`;
          ctx.lineWidth = 2;
        } else if (node.status === "DECOHERENT") {
          ctx.strokeStyle = "rgba(255, 51, 102, 0.3)";
          ctx.lineWidth = 1;
        } else {
          ctx.strokeStyle = "rgba(74, 85, 104, 0.2)";
          ctx.lineWidth = 1;
        }
        ctx.stroke();
      });
    }

    // Draw Nodes
    state.canvasNodes.forEach(node => {
      // Glow effect
      const glow = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, node.radius * 2.5);
      glow.addColorStop(0, node.color);
      glow.addColorStop(1, "transparent");

      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius * 2.5, 0, Math.PI * 2);
      ctx.fill();

      // Main Circle
      ctx.fillStyle = node.color;
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      ctx.fill();

      // Label text
      ctx.fillStyle = "#e2e8f0";
      ctx.font = "10px 'Fira Code', monospace";
      ctx.fillText(node.name, node.x + node.radius + 6, node.y + 3);

      if (node.status !== "ROOT") {
        ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
        ctx.font = "9px 'Inter', sans-serif";
        ctx.fillText(`Δ${node.entropy.toFixed(2)} | ${node.latency}ms`, node.x + node.radius + 6, node.y + 16);
      }
    });

    requestAnimationFrame(render);
  }

  // UI Updates
  function updateDOM() {
    // Metrics
    document.getElementById("metric-superposed").innerText = state.metrics.superposed;
    document.getElementById("metric-collapsed").innerText = state.metrics.collapsed;
    document.getElementById("metric-decohered").innerText = state.metrics.decohered;
    document.getElementById("metric-fingerprint").innerText = state.metrics.fingerprint;

    // State Inspector
    const inspector = document.getElementById("state-inspector");
    const keys = Object.keys(state.rootState);
    document.getElementById("root-keys-count").innerText = `${keys.length} keys`;
    if (keys.length === 0) {
      inspector.innerHTML = '<div class="empty-state">No canonical variables committed yet.</div>';
    } else {
      inspector.innerHTML = JSON.stringify(state.rootState, null, 2);
    }

    // Timeline Cards
    const container = document.getElementById("timelines-container");
    const tls = Object.values(state.timelines).slice(-6).reverse();
    container.innerHTML = tls.map(tl => `
      <div class="timeline-card">
        <div class="tl-header">
          <span class="tl-title">${tl.name}</span>
          <span class="tl-badge ${tl.status}">${tl.status}</span>
        </div>
        <div class="tl-stat-row">
          <span>Latency</span>
          <span class="tl-stat-val">${tl.latencyMs} ms</span>
        </div>
        <div class="tl-stat-row">
          <span>Entropy</span>
          <span class="tl-stat-val">${tl.entropy.toFixed(3)}</span>
        </div>
        <div class="tl-stat-row">
          <span>Mutations</span>
          <span class="tl-stat-val">${tl.deltasCount} keys</span>
        </div>
        ${tl.error ? `<div class="tl-stat-row" style="color:#ff3366"><span>Reason</span><span>${tl.error.slice(0, 32)}...</span></div>` : ''}
      </div>
    `).join("");

    updateLayout();
  }

  function appendLog(type, text) {
    const feed = document.getElementById("event-feed");
    const div = document.createElement("div");
    let cls = "event-line";
    if (type.includes("COLLAPSE")) cls += " collapse";
    if (type.includes("DECOHER")) cls += " decohere";
    div.className = cls;
    div.innerText = `[${new Date().toLocaleTimeString()}] ${type}: ${text}`;
    feed.prepend(div);

    // Keep log max 40 items
    while (feed.children.length > 40) {
      feed.removeChild(feed.lastChild);
    }
  }

  // Load initial state
  async function fetchInitialState() {
    try {
      const res = await fetch("/api/state");
      const data = await res.json();
      state.rootState = data.rootState || {};
      state.metrics.fingerprint = data.rootFingerprint || "000000000000";
      state.timelines = data.timelines || {};
      recalculateMetrics();
      updateDOM();
    } catch (e) {
      console.warn("Could not fetch initial state", e);
    }
  }

  function recalculateMetrics() {
    const list = Object.values(state.timelines);
    state.metrics.superposed = list.filter(t => t.status === "SUPERPOSED").length;
    state.metrics.collapsed = list.filter(t => t.status === "COLLAPSED").length;
    state.metrics.decohered = list.filter(t => t.status === "DECOHERENT").length;
  }

  // Connect SSE
  function connectSSE() {
    const es = new EventSource("/api/events");
    const statusText = document.getElementById("conn-status-text");

    es.onopen = () => {
      statusText.innerText = "COHERENT (SSE CONNECTED)";
    };

    es.onerror = () => {
      statusText.innerText = "RECONNECTING...";
    };

    es.addEventListener("TIMELINE_FORKED", ev => {
      const data = JSON.parse(ev.data);
      state.timelines[data.timeline.id] = data.timeline;
      recalculateMetrics();
      appendLog("FORK", `Timeline '${data.timeline.name}' spawned`);
      updateDOM();
    });

    es.addEventListener("TIMELINE_SUPERPOSED", ev => {
      const data = JSON.parse(ev.data);
      if (state.timelines[data.timelineId]) {
        state.timelines[data.timelineId].status = "SUPERPOSED";
      }
      recalculateMetrics();
      appendLog("SUPERPOSE", `Branch ${data.timelineId} active`);
      updateDOM();
    });

    es.addEventListener("TIMELINE_DECOHERED", ev => {
      const data = JSON.parse(ev.data);
      if (state.timelines[data.timelineId]) {
        state.timelines[data.timelineId].status = "DECOHERENT";
        state.timelines[data.timelineId].error = data.reason;
      }
      recalculateMetrics();
      appendLog("DECOHERENCE", data.reason);
      updateDOM();
    });

    es.addEventListener("WAVEFUNCTION_COLLAPSED", ev => {
      const data = JSON.parse(ev.data);
      data.allTimelines.forEach(tl => {
        state.timelines[tl.id] = tl;
      });
      // Refresh state
      fetchInitialState();
      appendLog("COLLAPSE", `Reality converged onto '${data.winner.name}'!`);
    });

    es.addEventListener("ROOT_STATE_UPDATE", ev => {
      const data = JSON.parse(ev.data);
      state.rootState[data.key] = data.value;
      updateDOM();
    });
  }

  // Start visualizer
  fetchInitialState();
  connectSSE();
  render();
})();
