def execute_action(decision, event):
    if decision == "revoke":
        print("Simulated remediation: revoking role")
        return {
            "action": "revoke",
            "principal": event.get("principal"),
            "role": event.get("roleGranted")
        }

    if decision == "ignore":
        print("Simulated remediation: ignoring event")
        return {
            "action": "ignore"
        }

    print("Simulated remediation: no action required")
    return {
        "action": "none"
    }
