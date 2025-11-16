import os
from openai import OpenAI

SUMMARY_MODEL = "mistralai/Mistral-7B-Instruct-v0.2:featherless-ai"

summary_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)


def generate_summary(prompt: str) -> str:
    completion = summary_client.chat.completions.create(
        model=SUMMARY_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    # openai>=1.0 returns pydantic-like objects; message is an object
    content = completion.choices[0].message.content
    return content if isinstance(content, str) else str(content)


