import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")

groq_client = Groq(api_key=GROQ_API_KEY)


def generate_advice(incident: str, memories: list[str]) -> str:
    """Generate incident advice using recalled Hindsight memories."""

    if memories:
        memory_context = "\n\n".join(
            f"- {memory}" for memory in memories
        )
    else:
        memory_context = "No relevant historical incidents were found."

    prompt = f"""
You are RetryZero, an incident-response assistant for on-call engineers.

Your special ability is learning from previous incidents.

CURRENT INCIDENT:
{incident}

RELEVANT HISTORICAL MEMORY FROM HINDSIGHT:
{memory_context}

Analyze the incident using the historical memory.

Return your response in exactly this structure:

ALREADY FAILED:
- List fixes that previously failed for similar incidents.
- Explain briefly why they failed.
- If there are no known failed fixes, write "None recorded."

WORKED BEFORE:
- List fixes that previously worked for similar incidents.
- Explain briefly what worked.
- If there are no known successful fixes, write "None recorded."

RECOMMENDED NEXT STEP:
- Give the safest practical next troubleshooting step.
- Do NOT recommend a fix that historical memory shows repeatedly failed unless you clearly explain why the current situation is different.

IMPORTANT:
- Never invent historical incidents.
- Never claim something worked unless the memory says it worked.
- Treat historical memory as evidence, not certainty.
"""

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a precise production incident-response assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content