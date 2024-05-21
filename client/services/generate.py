import os
from typing import List

import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv

# OpenAI style prompt
OPENAI_PROMPT = """Context information is below.
---------------------
{context}
---------------------
Given the context information and not prior knowledge, answer the query in Korean.
Query: {question}
Answer in Korean:"""

# LLaMA-2 style prompt
LLAMA3_PROMPT = """<|start_header_id|>system<|end_header_id|>

You are an assistant for answering questions in Korean.
You are given the extracted parts of a long document and a question. Provide a conversational answer in Korean.
If you don't know the answer, just say "I do not know." Don't make up an answer.<|eot_id|>

<|start_header_id|>user<|end_header_id|>
using the retrieved documents we will prompt the model to generate our responses
Question:{question}
Context:
{context}<|eot_id|>

<|start_header_id|>assistant<|end_header_id|>
Answer in Korean:"""

LLAMA3_SEQUENCE = [
    "<|eot_id|>",
    "<|start_header_id|>",
    "<|end_header_id|>",
    "<|begin_of_text|>",
    "<|end_of_text|>",
]


def generate_answer(query: str, contexts: List[str]) -> str:
    # .env 설정해주세요 (.env.example 참고)
    load_dotenv()

    # OpenAI의 인터페이스를 따라하는 LLM 서버에 요청을 보냄
    openai_api_key = os.getenv("OPENAI_API_KEY") or "EMPTY"
    openai_api_base = os.getenv("OPENAI_API_BASE") or "EMPTY"

    if openai_api_key == "EMPTY":  # openai-api-compatible LLM server
        rag_prompt = LLAMA3_PROMPT
        stop_sequences = LLAMA3_SEQUENCE

    else:  # openai api
        openai_api_base = "https://api.openai.com"
        rag_prompt = OPENAI_PROMPT

    model = "gpt-3.5-turbo-instruct"
    max_tokens = 512
    temperature = 0.2
    # stop_sequences = LLAMA3_SEQUENCE

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

    response = requests.post(url=url, headers=headers, json=data, timeout=120).json()
    print(f"{response=}")
    output_text = response["choices"][0]["text"]

    return output_text
