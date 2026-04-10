from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL, MAX_TOKENS, TEMPERATURE
from prompts import SYSTEM_PROMPT, build_user_message

_client = OpenAI(api_key=OPENAI_API_KEY)


def generate_prd_stream(inputs: dict):
    """Yields streamed markdown chunks from OpenAI for progressive rendering."""
    user_message = build_user_message(inputs)

    stream = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        stream=True,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


def generate_prd(inputs: dict) -> str:
    """Returns the full generated PRD markdown (non-streaming fallback)."""
    user_message = build_user_message(inputs)

    response = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )

    return response.choices[0].message.content or ""
