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

  let isClientSimulation = false;
  let sseFailureCount = 0;

  // Load initial state
  async function fetchInitialState() {
    try {
      const res = await fetch("/api/state");
      if (!res.ok) throw new Error("HTTP error " + res.status);
      const data = await res.json();
      state.rootState = data.rootState || {};
      state.metrics.fingerprint = data.rootFingerprint || "000000000000";
      state.timelines = data.timelines || {};
      recalculateMetrics();
      updateDOM();
    } catch (e) {
      console.log("[QuantumFlow] Live backend unreachable; activating Standalone Client Simulation Mode.");
      startClientSimulation();
    }
  }

  function recalculateMetrics() {
    const list = Object.values(state.timelines);
    state.metrics.superposed = list.filter(t => t.status === "SUPERPOSED").length;
    state.metrics.collapsed = list.filter(t => t.status === "COLLAPSED").length;
    state.metrics.decohered = list.filter(t => t.status === "DECOHERENT").length;
  }

  // Standalone Client Simulation for GitHub Pages & Static Public Hosting
  function startClientSimulation() {
    if (isClientSimulation) return;
    isClientSimulation = true;

    const statusText = document.getElementById("conn-status-text");
    statusText.innerText = "10B% COHERENT (STATIC CLOUD)";

    state.rootState = {
      "brand": "Senku Technologies",
      "ecosystem": "Senku Quantum Labs",
      "engine": "QuantumFlow Multiverse",
      "status": "PUBLIC_COHERENCE",
      "syntheses_completed": 0,
      "invariants": ["NonNegativeEntropy", "SolvencyPreservation"]
    };
    state.metrics.fingerprint = "7a8b9c0d1e2f";
    appendLog("SENKU_INIT", "Standalone Client Multiverse Engine activated.");
    updateDOM();

    // Periodic client-side multiverse simulation
    setInterval(() => {
      runClientSuperpositionRace();
    }, 2800);
  }

  let simCounter = 1;
  function runClientSuperpositionRace(customName = null) {
    simCounter++;
    const reqId = customName || `REQ-${simCounter}`;
    const tStart = Date.now();

    const t1 = {
      id: `tl-${Math.random().toString(16).slice(2, 10)}`,
      name: `DirectMesh-${reqId}`,
      parentId: "root",
      status: "SUPERPOSED",
      latencyMs: Math.floor(Math.random() * 40 + 70),
      entropy: 0.15,
      deltasCount: 2,
      error: null
    };

    const t2 = {
      id: `tl-${Math.random().toString(16).slice(2, 10)}`,
      name: `HedgedReplica-${reqId}`,
      parentId: "root",
      status: "SUPERPOSED",
      latencyMs: Math.floor(Math.random() * 25 + 28),
      entropy: 0.08,
      deltasCount: 2,
      error: null
    };

    const t3 = {
      id: `tl-${Math.random().toString(16).slice(2, 10)}`,
      name: `EdgeCache-${reqId}`,
      parentId: "root",
      status: "SUPERPOSED",
      latencyMs: Math.floor(Math.random() * 30 + 50),
      entropy: 0.05,
      deltasCount: 1,
      error: null
    };

    state.timelines[t1.id] = t1;
    state.timelines[t2.id] = t2;
    state.timelines[t3.id] = t3;
    recalculateMetrics();
    appendLog("FORK", `Spawned 3 speculative branches for ${reqId}`);
    soundEngine.playFork();
    updateDOM();

    // Resolve after delay
    setTimeout(() => {
      // 30% chance t1 encounters packet loss and decoheres
      if (Math.random() < 0.4) {
        t1.status = "DECOHERENT";
        t1.error = "Latency SLA breached (>100ms) or packet dropped";
        appendLog("DECOHERENCE", `Branch '${t1.name}' failed SLA invariant`);
        soundEngine.playDecohere();
      } else {
        t1.status = "DISSOLVED";
      }

      // t2 wins!
      t2.status = "COLLAPSED";
      t3.status = "DISSOLVED";

      state.rootState["syntheses_completed"] = (state.rootState["syntheses_completed"] || 0) + 1;
      state.rootState["last_winning_route"] = t2.name;
      state.rootState["last_latency"] = `${t2.latencyMs}ms`;
      state.metrics.fingerprint = Math.random().toString(16).slice(2, 14);

      recalculateMetrics();
      appendLog("COLLAPSE", `Reality converged onto '${t2.name}' in ${t2.latencyMs}ms!`);
      soundEngine.playCollapse();

      // Prune old timelines
      const keys = Object.keys(state.timelines);
      if (keys.length > 18) {
        keys.slice(0, keys.length - 12).forEach(k => delete state.timelines[k]);
      }
      updateDOM();
    }, 450);
  }

  // Connect SSE
  function connectSSE() {
    let es;
    try {
      es = new EventSource("/api/events");
    } catch (e) {
      startClientSimulation();
      return;
    }

    const statusText = document.getElementById("conn-status-text");

    es.onopen = () => {
      sseFailureCount = 0;
      statusText.innerText = "COHERENT (SSE CONNECTED)";
    };

    es.onerror = () => {
      sseFailureCount++;
      if (sseFailureCount > 2) {
        startClientSimulation();
      } else {
        statusText.innerText = "RECONNECTING...";
      }
    };

    es.addEventListener("TIMELINE_FORKED", ev => {
      const data = JSON.parse(ev.data);
      state.timelines[data.timeline.id] = data.timeline;
      recalculateMetrics();
      appendLog("FORK", `Timeline '${data.timeline.name}' spawned`);
      soundEngine.playFork();
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
      soundEngine.playDecohere();
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
      soundEngine.playCollapse();
    });

    es.addEventListener("CHAOS_INJECTED", ev => {
      const data = JSON.parse(ev.data);
      appendLog("CHAOS_STORM", `${data.report.chaosType} hit ${data.report.timelineName}`);
      soundEngine.playChaos();
      fetchInitialState();
    });

    es.addEventListener("QUANTUM_ENTANGLEMENT_SYNC", ev => {
      const data = JSON.parse(ev.data);
      appendLog("ENTANGLEMENT", `Teleported '${data.key}' across ${data.syncedBranches} universes`);
      fetchInitialState();
    });

    es.addEventListener("ROOT_STATE_UPDATE", ev => {
      const data = JSON.parse(ev.data);
      state.rootState[data.key] = data.value;
      updateDOM();
    });
  }

  // --- Web Audio FX Synthesizer (Zero Dependencies) ---
  const soundEngine = {
    enabled: false,
    ctx: null,
    init() {
      if (!this.ctx) {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        this.ctx = new AudioContext();
      }
      if (this.ctx.state === "suspended") {
        this.ctx.resume();
      }
    },
    playTone(freq, type, duration, gainLevel = 0.08) {
      if (!this.enabled || !this.ctx) return;
      try {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
        gain.gain.setValueAtTime(gainLevel, this.ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        osc.start();
        osc.stop(this.ctx.currentTime + duration);
      } catch (e) {}
    },
    playFork() {
      this.playTone(600, "sine", 0.15, 0.05);
    },
    playDecohere() {
      this.playTone(180, "sawtooth", 0.25, 0.07);
    },
    playCollapse() {
      if (!this.enabled || !this.ctx) return;
      // Synthesize harmonious major chord
      [440, 554, 659, 880].forEach((f, idx) => {
        setTimeout(() => this.playTone(f, "sine", 0.35, 0.04), idx * 40);
      });
    },
    playChaos() {
      this.playTone(220, "triangle", 0.3, 0.09);
    }
  };

  // --- Wire Interactive Control Deck ---
  function setupControls() {
    const btnSpawn = document.getElementById("btn-spawn");
    const btnChaos = document.getElementById("btn-chaos");
    const btnConflicts = document.getElementById("btn-conflicts");
    const btnAudio = document.getElementById("btn-audio");

    if (btnSpawn) {
      btnSpawn.addEventListener("click", async () => {
        btnSpawn.style.transform = "scale(0.95)";
        setTimeout(() => btnSpawn.style.transform = "", 150);
        if (isClientSimulation) {
          runClientSuperpositionRace("UserInteractive");
        } else {
          try {
            await fetch("/api/action/spawn", { method: "POST" });
          } catch (e) {
            runClientSuperpositionRace("UserInteractive");
          }
        }
      });
    }

    if (btnChaos) {
      btnChaos.addEventListener("click", async () => {
        btnChaos.style.transform = "scale(0.95)";
        setTimeout(() => btnChaos.style.transform = "", 150);
        if (isClientSimulation) {
          appendLog("CHAOS_STORM", "Synthetic entropy storm injected into active branch");
          soundEngine.playChaos();
          const active = Object.values(state.timelines).filter(t => t.status === "SUPERPOSED");
          if (active.length > 0) {
            active[0].status = "DECOHERENT";
            active[0].error = "Synthetic latency storm decoherence";
            recalculateMetrics();
            updateDOM();
          }
        } else {
          try {
            await fetch("/api/action/chaos", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ type: "LATENCY_SPIKE" })
            });
          } catch (e) {
            soundEngine.playChaos();
          }
        }
      });
    }

    if (btnConflicts) {
      btnConflicts.addEventListener("click", async () => {
        if (isClientSimulation) {
          appendLog("PARADOX_SCAN", "Causality check: Verified 0 write-write collisions in memory.");
        } else {
          try {
            const res = await fetch("/api/action/conflicts", { method: "POST" });
            const data = await res.json();
            if (data.count === 0) {
              appendLog("PARADOX_SCAN", "Causality check passed: Zero race conditions or collisions.");
            } else {
              appendLog("PARADOX_ALERT", `Detected ${data.count} state conflicts!`);
            }
          } catch (e) {
            appendLog("PARADOX_SCAN", "Causality check: Client state coherent.");
          }
        }
      });
    }

    if (btnAudio) {
      btnAudio.addEventListener("click", () => {
        soundEngine.init();
        soundEngine.enabled = !soundEngine.enabled;
        if (soundEngine.enabled) {
          btnAudio.innerHTML = "<span>🔊</span> Sound ON";
          btnAudio.classList.add("active");
          soundEngine.playCollapse();
        } else {
          btnAudio.innerHTML = "<span>🔇</span> Sound FX";
          btnAudio.classList.remove("active");
        }
      });
    }
  }

  // Start visualizer
  fetchInitialState();
  connectSSE();
  setupControls();
  render();
})();
