import os
import logging
import re

from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent, LoopAgent, ParallelAgent
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool
from google.adk.models import Gemini
from google.genai import types
from google.adk.tools import exit_loop

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper


# ==============================
# Logging
# ==============================

logging.basicConfig(level=logging.INFO)

load_dotenv()
model_name = os.getenv("MODEL")

RETRY_OPTIONS = types.HttpRetryOptions(
    initial_delay=1,
    attempts=6
)


# ==============================
# Shared Tools
# ==============================

def replace_state(tool_context: ToolContext, field: str, content: str):
    tool_context.state[field] = content
    logging.info(f"[STATE UPDATED] {field}")
    return {"status": "success"}


def write_file(tool_context: ToolContext, filename: str, content: str):
    os.makedirs("verdict_reports", exist_ok=True)

    # sanitize filename
    safe_name = re.sub(r"[^\w\-]", "_", filename)
    path = os.path.join("verdict_reports", safe_name)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f"[FILE CREATED] {path}")
    return {"status": "success"}


# ==============================
# STEP 2 – Investigation (Parallel)
# ==============================

admirer_agent = Agent(
    name="admirer",
    model=Gemini(model=model_name, retry_options=RETRY_OPTIONS),
    description="Agent A – Positive Researcher",
    instruction="""
ROLE: The Admirer

TOPIC:
{ TOPIC? }

EXISTING DATA:
{ pos_data? }

Research ONLY achievements, strengths, reforms, positive legacy.

If insufficient, refine search using:
- "{TOPIC} achievements"
- "{TOPIC} reforms"
- "{TOPIC} accomplishments"
- "{TOPIC} positive impact"

Produce at least 5 substantial bullet points.

Save using replace_state:
field = "pos_data"
content = full bullet list
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        LangchainTool(
            tool=WikipediaQueryRun(
                api_wrapper=WikipediaAPIWrapper()
            )
        ),
        replace_state
    ],
)


critic_agent = Agent(
    name="critic",
    model=Gemini(model=model_name, retry_options=RETRY_OPTIONS),
    description="Agent B – Negative Researcher",
    instruction="""
ROLE: The Critic

TOPIC:
{ TOPIC? }

EXISTING DATA:
{ neg_data? }

Research ONLY failures, controversies, oppression, criticisms.

If insufficient, refine search using:
- "{TOPIC} controversy"
- "{TOPIC} criticism"
- "{TOPIC} failures"
- "{TOPIC} oppression"

Produce at least 5 substantial bullet points.

Save using replace_state:
field = "neg_data"
content = full bullet list
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[
        LangchainTool(
            tool=WikipediaQueryRun(
                api_wrapper=WikipediaAPIWrapper()
            )
        ),
        replace_state
    ],
)


investigation_team = ParallelAgent(
    name="investigation_team",
    sub_agents=[admirer_agent, critic_agent]
)


# ==============================
# STEP 3 – Trial & Review (Loop)
# ==============================

judge_agent = Agent(
    name="judge",
    model=Gemini(model=model_name, retry_options=RETRY_OPTIONS),
    description="Agent C – The Judge",
    instruction="""
ROLE: The Judge

POSITIVE DATA:
{ pos_data? }

NEGATIVE DATA:
{ neg_data? }

Count bullet points in each section.

If either side has fewer than 5:
    Clearly state which side is insufficient.
    DO NOT call exit_loop.

If both sides have at least 5 substantial bullet points:
    Call exit_loop.
    State: "Research balanced. Ending loop."
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[exit_loop],
)


trial_loop = LoopAgent(
    name="trial_loop",
    sub_agents=[
        investigation_team,
        judge_agent
    ],
    max_iterations=3
)


# ==============================
# STEP 4 – Verdict
# ==============================

verdict_agent = Agent(
    name="verdict_writer",
    model=Gemini(model=model_name, retry_options=RETRY_OPTIONS),
    description="Writes final structured verdict.",
    instruction="""
TOPIC:
{ TOPIC? }

POSITIVE DATA:
{ pos_data? }

NEGATIVE DATA:
{ neg_data? }

Write structured analytical report:

1. Historical Background
2. Strengths and Achievements
3. Failures and Criticisms
4. Balanced Historical Judgment

Be neutral and academic.

After generating full report,
call write_file tool:

filename = TOPIC + "_verdict.txt"
content = full report
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[write_file]
)


# ==============================
# Pipeline
# ==============================

history_trial_pipeline = SequentialAgent(
    name="history_trial_pipeline",
    sub_agents=[
        trial_loop,
        verdict_agent
    ]
)


# ==============================
# STEP 1 – Inquiry
# ==============================

root_agent = Agent(
    name="inquiry_agent",
    model=Gemini(model=model_name, retry_options=RETRY_OPTIONS),
    description="Step 1 – Inquiry",
    instruction="""
Welcome the user professionally.

Ask for a historical figure or event.

When user provides topic:
    Save using replace_state:
        field = "TOPIC"
    Confirm briefly.
    Transfer to history_trial_pipeline.
""",
    generate_content_config=types.GenerateContentConfig(temperature=0),
    tools=[replace_state],
    sub_agents=[history_trial_pipeline],
)


# ==============================
# RUN EXAMPLE
# ==============================

if __name__ == "__main__":
    topic = input("Enter historical topic: ")
    root_agent.run(topic)