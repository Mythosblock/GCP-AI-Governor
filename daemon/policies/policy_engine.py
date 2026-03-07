def evaluate_event(event):
    role = event.get("roleGranted")
    event_type = event.get("event_type")

    if role == "roles/owner":
        return "revoke"

    if role in [
        "roles/iam.serviceAccountAdmin",
        "roles/resourcemanager.projectIamAdmin",
        "roles/editor"
    ]:
        return "revoke"

    if role in [
        "roles/viewer",
        "roles/browser"
    ]:
        return "allow"

    if event_type in [
        "heartbeat",
        "healthcheck",
        "noop"
    ]:
        return "ignore"

    return "allow"
