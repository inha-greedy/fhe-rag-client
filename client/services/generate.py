import os
from typing import List

import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv

# OpenAI style prompt
OPENAI_PROMPT = """질문에 답하는 인공지능 어시스턴트입니다. 다음의 문맥 정보를 활용하여 질문에 답변하세요.
답변할 수 없다면 "모르겠습니다"라고 말하세요. 답변은 최대 3문장으로 간결하게 해주세요.

질문: {question}

문맥: {context}

답변:
"""

# LLaMA-2 style prompt
LLAMA2_PROMPT = """<<SYS>>
질문에 답하는 인공지능 어시스턴트입니다. 다음의 문맥 정보를 활용하여 질문에 답변하세요.
답변할 수 없다면 "모르겠습니다"라고 말하세요. 답변은 최대 3문장으로 간결하게 해주세요.
<</SYS>>

[INST]
질문: {question}

문맥: {context}
[/INST]
답변:
"""

LLAMA2_SEQUENCE = ["[INST]", "[/INST]"]


def generate_answer(query: str, contexts: List[str]) -> str:
    # .env 설정해주세요 (.env.example 참고)
    load_dotenv()

    # OpenAI의 인터페이스를 따라하는 LLM 서버에 요청을 보냄
    openai_api_key = os.getenv("OPENAI_API_KEY") or "EMPTY"
    openai_api_base = os.getenv("OPENAI_API_BASE") or "EMPTY"

    if openai_api_key == "EMPTY":  # openai-api-compatible LLM server
        rag_prompt = LLAMA2_PROMPT

    else:  # openai api
        openai_api_base = "https://api.openai.com"
        rag_prompt = OPENAI_PROMPT

    model = "gpt-3.5-turbo-instruct"
    max_tokens = 1024
    temperature = 0.6
    # stop_sequences = LLAMA2_SEQUENCE

    context = "\n".join(contexts)

    formatted_prompt = rag_prompt.format(question=query, context=context)

    url = openai_api_base + "/v1/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + openai_api_key,
    }

    data = {
        "model": model,
        "prompt": formatted_prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        # "stop": stop_sequences,
    }

    response = requests.post(url=url, headers=headers, json=data, timeout=20).json()
    print(f"{response=}")
    output_text = response["choices"][0]["text"]

    return output_text
