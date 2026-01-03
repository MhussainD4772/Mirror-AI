import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

HF_TOKEN = os.getenv("HF_TOKEN", "")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is required. Please set it in the root .env file")

SUMMARY_MODEL = "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"

summary_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)


def generate_summary(prompt: str) -> str:
    completion = summary_client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    # openai>=1.0 returns pydantic-like objects; message is an object
    content = completion.choices[0].message.content
    return content if isinstance(content, str) else str(content)


