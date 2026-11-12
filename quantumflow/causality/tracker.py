"""
QuantumFlow - Causality DAG & Audit Tracker.

Constructs Directed Acyclic Graphs of multiverse branching, tracks
cryptographic state deltas, and renders visual ASCII causal topologies.
"""

from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
from quantumflow.core.timeline import TimelineStatus


class CausalityNode:
    """A node in the causal tree."""
    def __init__(self, node_id: str, label: str, parent_id: Optional[str] = None):
        self.node_id = node_id
        self.label = label
        self.parent_id = parent_id
        self.children: List[CausalityNode] = []
        self.attributes: Dict[str, Any] = {}

    def add_child(self, child: CausalityNode) -> None:
        self.children.append(child)


class CausalityGraph:
    """Manages the causality DAG across universes."""

    def __init__(self):
        self.nodes: Dict[str, CausalityNode] = {
            "root": CausalityNode("root", "Canonical Root Reality", None)
        }

    def record_timeline(self, timeline_dict: Dict[str, Any]) -> CausalityNode:
        tid = timeline_dict["id"]
        parent_id = timeline_dict.get("parentId") or "root"
        label = f"{timeline_dict['name']} [{timeline_dict['status']}]"
        
        node = CausalityNode(tid, label, parent_id)
        node.attributes = {
            "status": timeline_dict["status"],
            "latencyMs": timeline_dict.get("latencyMs", 0),
            "entropy": timeline_dict.get("entropy", 0),
            "deltasCount": timeline_dict.get("deltasCount", 0),
            "error": timeline_dict.get("error")
        }

        self.nodes[tid] = node
        if parent_id in self.nodes:
            self.nodes[parent_id].add_child(node)
        return node

    def render_ascii(self) -> str:
        """Renders an ASCII tree visualization of the multiverse branches."""
        lines: List[str] = []
        root = self.nodes.get("root")
        if not root:
            return "Empty Causality Graph"

        def _traverse(node: CausalityNode, prefix: str = "", is_last: bool = True):
            status = node.attributes.get("status", "")
            badge = ""
            if status == TimelineStatus.COLLAPSED.value:
                badge = " [★ COLLAPSED TO REALITY]"
            elif status == TimelineStatus.DECOHERENT.value:
                badge = f" [✗ DECOHERED: {node.attributes.get('error', 'violation')}]"
            elif status == TimelineStatus.DISSOLVED.value:
                badge = " [◌ DISSOLVED]"
            elif status == TimelineStatus.SUPERPOSED.value:
                badge = " [⚡ SUPERPOSED]"

            connector = "└── " if is_last else "├── "
            if node.node_id == "root":
                lines.append("● ROOT REALITY (Canonical)")
            else:
                lines.append(f"{prefix}{connector}{node.label}{badge}")

            child_prefix = prefix + ("    " if is_last else "│   ")
            child_count = len(node.children)
            for idx, child in enumerate(node.children):
                _traverse(child, child_prefix, idx == (child_count - 1))

        _traverse(root)
        return "\n".join(lines)
