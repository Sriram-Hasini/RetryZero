from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from html import escape

from memory import arecall_memories, aretain_memory
from llm import generate_advice


app = FastAPI(
    title="RetryZero",
    description="An incident agent that learns from failed fixes."
)


HTML_PAGE = """
<!DOCTYPE html>
<html>

<head>

    <title>RetryZero</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #080d1a;
            color: #e5e7eb;
            margin: 0;
            padding: 40px 20px;
        }

        .container {
            max-width: 1050px;
            margin: auto;
        }

        .badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            background: #172554;
            color: #93c5fd;
            font-size: 12px;
            font-weight: bold;
            letter-spacing: .5px;
            margin-bottom: 18px;
        }

        h1 {
            font-size: 46px;
            margin: 0;
            color: #f8fafc;
        }

        .subtitle {
            color: #94a3b8;
            margin: 8px 0 30px;
            font-size: 16px;
        }

        .input-card,
        .memory-card,
        .result-card,
        .outcome-card {
            background: #0f1728;
            border: 1px solid #26344d;
            border-radius: 14px;
            padding: 24px;
            margin-top: 20px;
        }

        textarea {
            width: 100%;
            min-height: 130px;
            padding: 16px;
            background: #0b1220;
            border: 1px solid #334155;
            border-radius: 10px;
            color: #f8fafc;
            font-size: 16px;
            resize: vertical;
            outline: none;
        }

        textarea:focus {
            border-color: #3b82f6;
        }

        .primary-button {
            margin-top: 15px;
            padding: 13px 24px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
        }

        .primary-button:hover {
            background: #1d4ed8;
        }

        .memory-title {
            color: #60a5fa;
            font-size: 18px;
            font-weight: bold;
        }

        .memory-description {
            color: #94a3b8;
            margin-top: 8px;
        }

        .sections {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 18px;
            margin-top: 22px;
        }

        .section {
            padding: 20px;
            border-radius: 12px;
        }

        .failed {
            background: #241216;
            border: 1px solid #6b2630;
        }

        .worked {
            background: #10241c;
            border: 1px solid #236044;
        }

        .recommended {
            margin-top: 18px;
            padding: 20px;
            border-radius: 12px;
            background: #111e35;
            border: 1px solid #28528c;
        }

        .section-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 14px;
        }

        .failed .section-title {
            color: #f87171;
        }

        .worked .section-title {
            color: #4ade80;
        }

        .recommended .section-title {
            color: #60a5fa;
        }

        .item {
            margin: 10px 0;
            line-height: 1.5;
            color: #dbe4f0;
        }

        .outcome-card {
            text-align: center;
        }

        .outcome-title {
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 8px;
        }

        .outcome-description {
            color: #94a3b8;
            margin-bottom: 18px;
        }

        .worked-button,
        .failed-button {
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            cursor: pointer;
            margin: 5px;
        }

        .worked-button {
            background: #15803d;
        }

        .worked-button:hover {
            background: #166534;
        }

        .failed-button {
            background: #b91c1c;
        }

        .failed-button:hover {
            background: #991b1b;
        }

        .success-message {
            background: #10241c;
            border: 1px solid #236044;
            color: #86efac;
            padding: 18px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .error-message {
            background: #241216;
            border: 1px solid #6b2630;
            color: #fca5a5;
            padding: 18px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .memory-count {
            display: inline-block;
            padding: 5px 10px;
            background: #172554;
            color: #93c5fd;
            border-radius: 20px;
            font-size: 13px;
            margin-top: 10px;
        }

        @media (max-width: 750px) {

            body {
                padding: 25px 15px;
            }

            h1 {
                font-size: 36px;
            }

            .sections {
                grid-template-columns: 1fr;
            }

        }

    </style>

</head>


<body>

<div class="container">

    <div class="badge">
        HINDSIGHT MEMORY ACTIVE
    </div>

    <h1>RetryZero</h1>

    <div class="subtitle">
        An incident agent that remembers what failed — so your team doesn't repeat it.
    </div>


    <div class="input-card">

        <form method="post" action="/advice">

            <textarea
                name="incident"
                placeholder="Describe the incident...

Example:
payments-api returning 504 on checkout"
                required
            ></textarea>

            <button class="primary-button" type="submit">
                Get Incident Advice
            </button>

        </form>

    </div>


    {RESULT}

</div>

</body>

</html>
"""


def render_item_list(items):
    """Convert simple text lines into HTML list items."""

    if not items:
        return "<div class='item'>None recorded.</div>"

    html = ""

    for item in items:
        cleaned = item.strip()

        if cleaned:
            html += f"<div class='item'>• {escape(cleaned)}</div>"

    return html


def parse_advice(advice):
    """
    Extract the three sections from the LLM response.
    """

    failed = []
    worked = []
    recommended = []

    current = None

    for raw_line in advice.splitlines():

        line = raw_line.strip()

        if not line:
            continue

        upper = line.upper()

        if "ALREADY FAILED" in upper:
            current = "failed"
            continue

        if "WORKED BEFORE" in upper:
            current = "worked"
            continue

        if "RECOMMENDED NEXT STEP" in upper:
            current = "recommended"
            continue

        if line.startswith("-"):
            line = line.lstrip("-").strip()

        if line.startswith("*"):
            line = line.lstrip("*").strip()

        if current == "failed":
            failed.append(line)

        elif current == "worked":
            worked.append(line)

        elif current == "recommended":
            recommended.append(line)

    return failed, worked, recommended


@app.get("/", response_class=HTMLResponse)
def home():

    return HTML_PAGE.replace(
        "{RESULT}",
        ""
    )

@app.post("/advice", response_class=HTMLResponse)
async def get_advice(incident: str = Form(...)):

    try:

        memories = await arecall_memories(incident)

        # Keep the most relevant Hindsight memories for focused reasoning
        memories = memories[:12]

        memory_texts = []

        for memory in memories:

            try:
                memory_texts.append(memory.text)

            except AttributeError:
                memory_texts.append(str(memory))

        advice = generate_advice(
            incident,
            memory_texts
        )

        failed, worked, recommended = parse_advice(advice)

        result_html = f"""

        <div class="memory-card">

            <div class="memory-title">
                Hindsight Memory Retrieved
            </div>

            <div class="memory-description">
                RetryZero searched historical incident experience before
                generating this recommendation.
            </div>

            <div class="memory-count">
                {len(memory_texts)} relevant memories recalled
            </div>

        </div>


        <div class="result-card">

            <div class="sections">

                <div class="section failed">

                    <div class="section-title">
                        🔴 Already Failed
                    </div>

                    {render_item_list(failed)}

                </div>


                <div class="section worked">

                    <div class="section-title">
                        🟢 Worked Before
                    </div>

                    {render_item_list(worked)}

                </div>

            </div>


            <div class="recommended">

                <div class="section-title">
                    🔵 Recommended Next Step
                </div>

                {render_item_list(recommended)}

            </div>

        </div>


        <div class="outcome-card">

            <div class="outcome-title">
                Did the recommended fix work?
            </div>

            <div class="outcome-description">
                Your answer becomes new Hindsight memory.
            </div>


            <form method="post" action="/outcome">

                <input
                    type="hidden"
                    name="incident"
                    value="{escape(incident)}"
                >

                <input
                    type="hidden"
                    name="advice"
                    value="{escape(advice)}"
                >


                <button
                    class="worked-button"
                    type="submit"
                    name="outcome"
                    value="worked"
                >
                    ✓ It Worked
                </button>


                <button
                    class="failed-button"
                    type="submit"
                    name="outcome"
                    value="failed"
                >
                    ✕ It Failed
                </button>

            </form>

        </div>

        """

        return HTML_PAGE.replace(
            "{RESULT}",
            result_html
        )

    except Exception as error:

        error_html = f"""

        <div class="error-message">

            <strong>RetryZero encountered an error.</strong>

            <br><br>

            {escape(str(error))}

        </div>

        """

        return HTML_PAGE.replace(
            "{RESULT}",
            error_html
        )


    except Exception as error:

        error_html = f"""

        <div class="error-message">

            <strong>RetryZero encountered an error.</strong>

            <br><br>

            {escape(str(error))}

        </div>

        """

        return HTML_PAGE.replace(
            "{RESULT}",
            error_html
        )


@app.post("/outcome", response_class=HTMLResponse)
async def record_outcome(
    incident: str = Form(...),
    advice: str = Form(...),
    outcome: str = Form(...)
):

    try:

        if outcome not in ["worked", "failed"]:
            raise ValueError("Invalid outcome.")

        if outcome == "failed":

            outcome_text = f"""
RETRYZERO OUTCOME MEMORY

INCIDENT PATTERN:
{incident}

AGENT RECOMMENDATION:
{advice}

ENGINEER OUTCOME:
FAILED

LEARNING:
This recommendation was explicitly attempted by the engineer and FAILED
to resolve this incident pattern.

FUTURE GUIDANCE:
Do NOT repeat this recommendation automatically for the same or a closely
related incident pattern. Treat this recommendation as a previously failed
approach and prefer alternative actions supported by successful historical
evidence.
"""

        else:

            outcome_text = f"""
RETRYZERO OUTCOME MEMORY

INCIDENT PATTERN:
{incident}

AGENT RECOMMENDATION:
{advice}

ENGINEER OUTCOME:
WORKED

LEARNING:
This recommendation was explicitly attempted by the engineer and WORKED
for this incident pattern.

FUTURE GUIDANCE:
This recommendation can be considered a previously successful approach
for the same or a closely related incident pattern, while still validating
current system conditions before applying it.
"""

        # Store the structured outcome in Hindsight
        await aretain_memory(outcome_text)

        if outcome == "worked":

            message = """
            <div class="success-message">

                ✓ Outcome recorded as <strong>WORKED</strong>.

                <br><br>

                <strong>Hindsight learned:</strong>
                this approach succeeded for this incident pattern.

                <br><br>

                <strong>Next time:</strong>
                RetryZero can use this outcome as positive historical evidence.

            </div>
            """

        else:

            message = """
            <div class="error-message">

                ✕ Outcome recorded as <strong>FAILED</strong>.

                <br><br>

                <strong>Hindsight learned:</strong>
                this approach failed for this incident pattern.

                <br><br>

                <strong>Next time:</strong>
                RetryZero can use this outcome as negative historical evidence
                and avoid repeating it blindly.

            </div>
            """

        return HTML_PAGE.replace(
            "{RESULT}",
            message
        )

    except Exception as error:

        error_html = f"""
        <div class="error-message">

            <strong>Could not save the outcome.</strong>

            <br><br>

            {escape(str(error))}

        </div>
        """

        return HTML_PAGE.replace(
            "{RESULT}",
            error_html
        )