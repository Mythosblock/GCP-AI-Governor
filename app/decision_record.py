from __future__ import annotations

import os
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass
class EventContext:
    source: Optional[str] = None
    type: Optional[str] = None
    subject: Optional[str] = None
    time: Optional[str] = None
    service_name: Optional[str] = None
    method_name: Optional[str] = None
    resource_name: Optional[str] = None
    principal_email: Optional[str] = None


@dataclass
class ResourceContext:
    project_id: Optional[str] = None
    location: Optional[str] = None
    target_type: Optional[str] = None
    target_name: Optional[str] = None


@dataclass
class DeterministicPolicyContext:
    matched: bool = False
    rule_id: Optional[str] = None
    rules_fired: List[str] = field(default_factory=list)


@dataclass
class VertexAdvisoryContext:
    enabled: bool = False
    status: str = "skipped"
    model: Optional[str] = None
    latency_ms: int = 0
    summary: Optional[str] = None
    error: Optional[str] = None


@dataclass
class KafkaContext:
    enabled: bool = False
    status: str = "skipped"
    topic: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ActionResultContext:
    executed: bool = False
    action: str = "none"
    status: str = "UNKNOWN"
    dry_run: bool = True


@dataclass
class RuntimeContext:
    region: Optional[str] = None
    revision: Optional[str] = None
    instance_id: Optional[str] = None


@dataclass
class DecisionRecord:
    governor_version: str = "v1.0.0"
    service: str = "daemonic-codex-ai-governor"
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    timestamp: str = field(default_factory=_now_iso)
    live_mode: bool = False
    evaluation_mode: str = "deterministic_only"
    status: str = "UNKNOWN"
    decision: str = "unknown"
    reason: str = "unspecified"
    risk_level: str = "unknown"
    summary: str = "Decision recorded."
    event: EventContext = field(default_factory=EventContext)
    resource: ResourceContext = field(default_factory=ResourceContext)
    deterministic_policy: DeterministicPolicyContext = field(default_factory=DeterministicPolicyContext)
    vertex_advisory: VertexAdvisoryContext = field(default_factory=VertexAdvisoryContext)
    kafka: KafkaContext = field(default_factory=KafkaContext)
    action_result: ActionResultContext = field(default_factory=ActionResultContext)
    runtime: RuntimeContext = field(default_factory=lambda: RuntimeContext(
        region=os.environ.get("REGION", "us-central1"),
        revision=os.environ.get("K_REVISION"),
        instance_id=os.environ.get("K_INSTANCE"),
    ))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
