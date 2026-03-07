import os
import json
import logging
import vertexai
from vertexai.generative_models import GenerativeModel, Part, Tool, FunctionDeclaration
from functions_framework import cloud_event
from cloudevents.http import CloudEvent
from google.cloud import logging as cloud_logging

# --- Configuration & State ---
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT", "numeric-axe-zll0l")
REGION = os.environ.get("REGION", "us-central1")
LIVE_MODE = os.environ.get("LIVE_MODE", "false").lower() == "true"
MAX_ITERATIONS = int(os.environ.get("MAX_ITERATIONS", "8"))

# --- Telemetry Setup ---
logging_client = cloud_logging.Client(project=PROJECT_ID)
logging_client.setup_logging()
logger = logging.getLogger("gcp-ai-governor")

def structured_log(entry: dict):
    """Emits parseable JSON to Cloud Logging for audit/BigQuery sinks."""
    logger.info(json.dumps(entry))

# --- Vertex AI Initialization ---
vertexai.init(project=PROJECT_ID, location=REGION)

# 1. Define the strict schema for the LLM Tool
link_billing_func = FunctionDeclaration(
    name="link_billing_account",
    description="Links a GCP project to an organization billing account.",
    parameters={
        "type": "object",
        "properties": {
            "project_id": {"type": "string", "description": "The target GCP project ID"},
            "billing_account": {"type": "string", "description": "The billing account ID"}
        },
        "required": ["project_id", "billing_account"]
    }
)
governance_tool = Tool(function_declarations=[link_billing_func])

# Initialize the model 
model = GenerativeModel("gemini-2.5-flash", tools=[governance_tool])

def execute_tool(name: str, args: dict) -> dict:
    """Executes the tool, hard-enforcing the DRY_RUN airgap."""
    if name == "link_billing_account":
        if not LIVE_MODE:
            return {"status": "DRY_RUN_SUCCESS", "action": "link_billing", "args": args}
        
        # LIVE EXECUTION PATH (Insert Orchestrator SA Impersonation logic here)
        return {"status": "EXECUTED", "action": "link_billing", "args": args}
    
    return {"error": f"Unknown tool requested: {name}"}

@cloud_event
def daemon_entry(event: CloudEvent):
    """Eventarc Cloud Run Entrypoint"""
    payload = event.data
    proto = payload.get("protoPayload", {})
    
    # Safely extract context from Audit Log payload
    method_name = proto.get("methodName", "UNKNOWN")
    principal = proto.get("authenticationInfo", {}).get("principalEmail", "UNKNOWN")
    
    # Try multiple paths for projectId depending on the exact Audit Log type
    project_id = (
        proto.get("request", {}).get("project", {}).get("projectId")
        or (proto.get("resourceName", "").split("/")[-1] if proto.get("resourceName") else "UNKNOWN")
    )

    prompt = f"""
    You are the GCP AI Governor.
    Event Detected: {method_name} by {principal} on project {project_id}.
    Evaluate governance posture. If this is a project creation, ensure billing is linked.
    You must use the provided tools to take action. Default to safe operations.
    """

    # Start multi-turn history with the Vertex API Parts
    contents = [Part.from_text(prompt)]
    transcript = {"live_mode": LIVE_MODE, "steps": []}

    # The Manual ReAct Loop Guardrail
    for iteration in range(MAX_ITERATIONS):
        response = model.generate_content(contents)
        
        # 1. Append the model's raw response to the history to maintain conversation state
        contents.append(response.candidates[0].content)

        step_log = {"iteration": iteration + 1, "tool_calls": []}

        # 2. Check if the model decided to call a function
        if response.function_calls:
            for function_call in response.function_calls:
                tool_name = function_call.name
                
                # Convert protobuf map to standard dict
                tool_args = {key: val for key, val in function_call.args.items()}
                
                # Execute the tool
                observation = execute_tool(tool_name, tool_args)
                step_log["tool_calls"].append({"name": tool_name, "args": tool_args, "observation": observation})
                
                # 3. Append the observation back to the prompt history as a Part
                contents.append(
                    Part.from_function_response(
                        name=tool_name,
                        response=observation
                    )
                )
        else:
            # No function calls = model has reached a final conclusion. Break the loop.
            transcript["final_decision"] = response.text
            step_log["final_decision"] = response.text
            transcript["steps"].append(step_log)
            break

        transcript["steps"].append(step_log)
    else:
        # Hit Max Iterations guardrail without a clean break
        transcript["final_decision"] = "ABORTED_MAX_ITERATIONS"

    # Emit the final structured log of the entire "thought process"
    structured_log({"type": "governance_transcript", "target_project": project_id, "transcript": transcript})

    return ("OK", 200)
