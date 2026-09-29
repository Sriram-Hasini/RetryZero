import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

load_dotenv()

HINDSIGHT_BASE_URL = os.getenv(
    "HINDSIGHT_BASE_URL",
    "https://api.hindsight.vectorize.io"
)

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BANK = os.getenv("HINDSIGHT_BANK", "retryzero")

if not HINDSIGHT_API_KEY:
    raise ValueError("HINDSIGHT_API_KEY is missing from .env")

client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY
)


# ---------------------------------------------------------
# SYNC FUNCTIONS
# Used only by seed.py and command-line testing
# ---------------------------------------------------------

def retain_memory(content: str):
    return client.retain(
        bank_id=HINDSIGHT_BANK,
        content=content
    )


def recall_memories(query: str):
    result = client.recall(
        bank_id=HINDSIGHT_BANK,
        query=query
    )

    return result.results


# ---------------------------------------------------------
# ASYNC FUNCTIONS
# Used by FastAPI
# ---------------------------------------------------------

async def aretain_memory(content: str):
    return await client.aretain(
        bank_id=HINDSIGHT_BANK,
        content=content
    )


async def arecall_memories(query: str):
    result = await client.arecall(
        bank_id=HINDSIGHT_BANK,
        query=query
    )

    return result.results


def close_memory():
    client.close()