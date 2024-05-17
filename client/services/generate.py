import os
from dotenv import load_dotenv
import requests

# OpenAI stype prompt
OPENAI_PROMPT = """
[ SYSTEM ]
당신은 Human을 도와주는 친절한 AI 비서입니다. Human의 질문을 해결하는 유용한 대답을 만들어 주세요.
답변을 위해 3 backticks로 감싼 context 정보를 사용할 수 있습니다. (정보는 제공되지 않을 수도 있습니다.)

```context
{context}
```

[ Human ]
{question}

[ AI 비서 ]
"""

# LLaMA-2 style prompt
LLAMA2_PROMPT = """<<SYS>>
당신은 Human을 도와주는 친절한 AI 비서입니다. Human의 질문을 해결하는 유용한 대답을 만들어 주세요.
답변을 위해 3 backticks로 감싼 context 정보를 사용할 수 있습니다. (정보는 제공되지 않을 수도 있습니다.)

```context
{context}
```

<</SYS>>

[INST]
Human: {question}
[/INST]
AI 비서: 
"""

LLAMA2_SEQUENCE = "[INST]"


def generate_answer(query: str, context: str) -> str:

    # .env 설정해주세요 (.env.example 참고)
    load_dotenv()

    # OpenAI의 인터페이스를 따라하는 LLM 서버에 요청을 보냄
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key is "EMPTY" or None:
        # openai-api-compatible LLM server
        openai_api_base = os.getenv("OPENAI_API_BASE")
        rag_prompt = LLAMA2_PROMPT
    else:
        # openai api
        openai_api_base = "https://api.openai.com"
        rag_prompt = OPENAI_PROMPT

    model = "gpt-3.5-turbo-instruct"
    max_tokens = 200
    temperature = 0.1
    stop_sequences = [
        LLAMA2_SEQUENCE,
    ]

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
        "stop": stop_sequences,
    }

    response = requests.post(url=url, headers=headers, json=data, timeout=120).json()

    output_text = response["choices"][0]["text"]

    return output_text
