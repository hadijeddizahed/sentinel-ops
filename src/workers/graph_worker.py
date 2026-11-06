"""Graph Worker: Microservice dependency and blast-radius analyzer using NetworkX."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import networkx as nx
import json

# TODO: Milestone 3: Ingest data/topology.json and implement blast radius traversal

class GraphWorker:
    """Constructs an in-memory enterprise dependency graph from topology.json
       and calculates the blast radius and on-call escalation list for outages.
    """

    def __init__(self, topology_path: Path | str |None = None) -> None:
        if topology_path is None:
            self.topology_path = (
                    Path(__file__).resolve().parent.parent.parent / "data" / "topology.json"
            )
        else:
            self.topology_path = Path(topology_path)
        self.graph = nx.DiGraph()
        self._build_graph_from_topology()

    def _build_graph_from_topology(self) -> None:
        """Parses topology.json and constructs directed dependency edges."""
        if not self.topology_path.exists():
            print("topology.json not found")
            return
        with open(self.topology_path, "r", encoding="utf-8") as topology_file:
            data: dict[str, Any] = json.load(topology_file)

        # add datastore nodes
        for ds in data.get("datastores", []):
            self.graph.add_node(
                ds["name"],
                node_type="datastore",
                db_type=ds["type"],
                lead = ds.get("lead", None),
            )

        # add service nodes and directed edges
        for svc in data.get("services", []):
            svc_name = svc["name"]
            self.graph.add_node(
                svc_name,
                node_type="service",
                team = svc["team"],
                lead = svc["lead"],
            )

            # Add dependency edges
            for dep in svc.get("depends_on", []):
                self.graph.add_edge(svc_name, dep, relation="DEPENDS_ON")

    def get_blast_radius(self, failing_component: str) -> dict[str, Any]:
        """Calculates the upstream impact when a specific service or database fails.
                If Component B fails, any Component A where A depends on B is affected!
                In NetworkX, this means traversing incoming edges (predecessors / reverse traversal).
        """
        if failing_component not in self.graph:
            return {
                "error": f"Component '{failing_component}' not found in topology graph.",
                "failing_component": failing_component,
                "impacted_services": [],
                "oncall_leads": [],
            }
        # Find all upstream services that depend directly or indirectly on this component
        # We reverse the graph directions to trace outwards from the failure point
        reversed_graph = self.graph.reverse()
        impacted_nodes = list(
            nx.descendants(reversed_graph, failing_component)
        )

        # Collect unique on-call leads and teams affected
        oncall_leads: list[dict[str, str]] = []
        seen_leads = set()
        # Check the failing component's own lead first
        failing_lead = self.graph.nodes[failing_component].get("lead")
        if failing_lead and failing_lead not in seen_leads:
            seen_leads.add(failing_lead)
            oncall_leads.append(
                {
                    "lead": failing_lead,
                    "service": failing_component,
                    "role": "Owner (Primary Fixer)",
                }
            )
        # Check downstream affected leads
        for node in impacted_nodes:
            lead = self.graph.nodes[node].get("lead")
            if lead and lead not in seen_leads:
                seen_leads.add(lead)
                oncall_leads.append(
                    {
                        "lead": lead,
                        "service": node,
                        "role": "Impacted Consumer",
                    }
                )
        return {
            "failing_component": failing_component,
            "total_impacted_count": len(impacted_nodes),
            "impacted_services": impacted_nodes,
            "oncall_leads": oncall_leads,
        }



