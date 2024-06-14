import os
from typing import List
from openai import OpenAI

from dotenv import load_dotenv

# OpenAI style prompt
OPENAI_PROMPT = """Recent-information context is below.
---
{context}
---
Given the context information and not prior knowledge, answer the query in Korean.
do not use markdown format."""


def generate_answer(query: str, contexts: List[str]) -> str:
    # .env 설정해주세요 (.env.example 참고)
    load_dotenv()

    # OpenAI의 인터페이스를 따라하는 LLM 서버에 요청을 보냄
    openai_api_key = os.getenv("OPENAI_API_KEY") or "EMPTY"

    model = "gpt-4o-2024-05-13"

    rag_prompt = OPENAI_PROMPT

    context = "\n".join(contexts)

    formatted_prompt = rag_prompt.format(question=query, context=context)
    print(f"{formatted_prompt=}")

    client = OpenAI(api_key=openai_api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": query},
        ],
        temperature=0.5,
    )

    print(f"{response=}")
    output_text = response.choices[0].message.content

    return output_text
