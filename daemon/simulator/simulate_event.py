import requests

event = {
    "event_type": "iam.roleGranted",
    "principal": "test-user",
    "resource": "projects/mythosblock-core",
    "roleGranted": "roles/owner"
}

response = requests.post(
    "http://127.0.0.1:8080/event",
    json=event,
    timeout=10
)

print(response.json())
