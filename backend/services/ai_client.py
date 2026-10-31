import os

from dotenv import load_dotenv
from openai import OpenAI


NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "nvidia/nemotron-3.5-lightning-30b-a3b"


def get_ai_client() -> OpenAI:
    """Create the NVIDIA-compatible client only when an AI request is made."""
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    if not api_key:
        raise RuntimeError("NVIDIA_API_KEY is not configured.")
    return OpenAI(base_url=NVIDIA_BASE_URL, api_key=api_key)
