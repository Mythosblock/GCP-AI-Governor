from pathlib import Path

repo_main = Path.home() / "Mythosblock" / "repos" / "GCP-AI-Governor" / "app" / "main.py"
text = repo_main.read_text()

import_line = "from app.decision_record import DecisionRecord, EventContext, ResourceContext, DeterministicPolicyContext, VertexAdvisoryContext, KafkaContext, ActionResultContext\n"
if "from app.decision_record import DecisionRecord" not in text:
    lines = text.splitlines()
    insert_at = 0
    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1
    lines.insert(insert_at, import_line.rstrip("\n"))
    text = "\n".join(lines) + "\n"

marker = "def governor("
if marker not in text:
    raise SystemExit("Could not find governor function in app/main.py")

if "_decision_record = DecisionRecord(" in text:
    print("DecisionRecord patch already present.")
    repo_main.write_text(text)
    raise SystemExit(0)

start = text.index(marker)
body_start = text.index(":", start) + 1

injection = """

    _decision_record = DecisionRecord(
        live_mode=LIVE_MODE,
        event=EventContext(),
        resource=ResourceContext(
            project_id=os.environ.get("GOOGLE_CLOUD_PROJECT", "unknown"),
            location=os.environ.get("REGION", "us-central1"),
        ),
        deterministic_policy=DeterministicPolicyContext(),
        vertex_advisory=VertexAdvisoryContext(
            enabled=os.environ.get("ENABLE_VERTEX_REASONING", "false").lower() == "true",
            model=os.environ.get("VERTEX_MODEL_ID", "gemini-2.5-flash"),
        ),
        kafka=KafkaContext(
            enabled=bool(os.environ.get("KAFKA_BOOTSTRAP_SERVERS")),
            status="enabled" if os.environ.get("KAFKA_BOOTSTRAP_SERVERS") else "skipped",
            topic=os.environ.get("KAFKA_TOPIC"),
            error=None if os.environ.get("KAFKA_BOOTSTRAP_SERVERS") else "No bootstrap servers configured",
        ),
        action_result=ActionResultContext(
            executed=False,
            action="none",
            status="UNKNOWN",
            dry_run=(not LIVE_MODE),
        ),
    )
"""

text = text[:body_start] + injection + text[body_start:]

return_replacements = [
    (
        'return {"status": "ok",',
        '''_decision_record.status = "OK"
    _decision_record.decision = "allow"
    _decision_record.reason = "service_health"
    _decision_record.risk_level = "low"
    _decision_record.summary = "Governor health response emitted."
    try:
        structured_log(_decision_record.to_dict())
    except Exception:
        pass
    return {"status": "ok",'''
    ),
    (
        'return response',
        '''try:
        if isinstance(response, dict):
            _decision_record.status = str(response.get("status", _decision_record.status)).upper()
            evaluation = response.get("evaluation", {})
            action_result = response.get("action_result", {})
            _decision_record.decision = str(evaluation.get("decision", _decision_record.decision))
            _decision_record.reason = str(evaluation.get("reason", _decision_record.reason))
            _decision_record.risk_level = str(evaluation.get("risk_level", _decision_record.risk_level))
            _decision_record.evaluation_mode = str(evaluation.get("evaluation_mode", _decision_record.evaluation_mode))
            _decision_record.summary = str(evaluation.get("summary", _decision_record.summary))
            _decision_record.event_id = response.get("event_id")
            _decision_record.request_id = response.get("request_id", _decision_record.request_id)
            _decision_record.action_result = ActionResultContext(
                executed=bool(action_result.get("executed", False)),
                action=str(action_result.get("action", "none")),
                status=str(action_result.get("status", _decision_record.status)),
                dry_run=bool(action_result.get("dry_run", not LIVE_MODE)),
            )
        structured_log(_decision_record.to_dict())
    except Exception:
        pass
    return response'''
    ),
]

for old, new in return_replacements:
    if old in text:
        text = text.replace(old, new, 1)

repo_main.write_text(text)
print("Patched app/main.py successfully.")
