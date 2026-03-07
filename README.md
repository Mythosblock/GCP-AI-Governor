# gcp-ai-governor

Local simulation environment for an AI cloud governance agent.

## Verified control loop target

event -> evaluation -> decision -> simulated remediation

## Project structure

- daemon/main.py
- daemon/policies/policy_engine.py
- daemon/tools/actions.py
- daemon/simulator/simulate_event.py

## Local run

Activate the environment:

source ~/gcp-ai-governor/.venv/bin/activate

Start the agent:

python3 ~/gcp-ai-governor/daemon/main.py

Run the simulator in a second terminal:

python3 ~/gcp-ai-governor/daemon/simulator/simulate_event.py
