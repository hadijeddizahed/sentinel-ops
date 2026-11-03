"""Pydantic data schemas and contracts for SentinelOps."""

from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class IncidentAlert(BaseModel):
    """Incident Alert model."""
    service_name: str
    severity: Literal['CRITICAL', "HIGH", "MEDIUM", "LOW"] # CRITICAL, HIGH, MEDIUM, LOW
    error_code: str
    raw_error_log: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class SupervisorPlan(BaseModel):
    """Supervisor Plan model."""
    needs_runbook: bool = True
    needs_blast_radius: bool = True
    needs_log_analysis: bool = True
    reasoning: str = ""

class IncidentPostMortem(BaseModel):
    """Incident Post-Mortem model."""
    root_cause: str
    blast_radius_services: list[str]
    oncall_contacts: list[str]
    mitigation_steps: list[str]
    p95_latency_ms: float| None = None
    p99_latency_ms: float| None = None
    confidence_score: float= Field(ge=0.0, le=1.0)

class InvestigationState(BaseModel):
    """The shared memory state passing between workers and supervisor."""
    alert: IncidentAlert
    plan: SupervisorPlan | None = None
    runbook_context: list[str] = Field(default_factory=list)
    impacted_services: list[str] = Field(default_factory=list)
    contacts_to_notify: list[str] = Field(default_factory=list)
    log_metrics: list[str] = Field(default_factory=list)
    post_mortem: IncidentPostMortem | None = None

