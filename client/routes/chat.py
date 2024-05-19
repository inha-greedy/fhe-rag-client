from fastapi import APIRouter, Form

from ..services.chat import (
    choose_indices,
    decrypt_similarities,
    get_similarities_from_server,
    send_indices_and_receive_contexts,
)
from ..services.generate import generate_answer
from ..services.session import set_content, pop_content

chat_router = APIRouter()


@chat_router.post("/chat")
async def chat(query: str = Form(...), step: int = Form(...)):
    if step == 1:  # send query to storage-server and receive similarities
        encrypted_similarities = get_similarities_from_server(query=query)

        print(f"{encrypted_similarities=}")
        set_content("c1", encrypted_similarities)

    elif step == 2:  # decrypt similarity
        encrypted_similarities = pop_content("c1")
        similarities, avg_time = decrypt_similarities(encrypted_similarities=encrypted_similarities)

        print(f"{similarities=}")
        set_content("c2", similarities)

        no_sync = pop_content("no_sync") or False
        set_content("no_sync", no_sync)

        return {"avg_decrypt_time": avg_time, "no_sync": no_sync}

    elif step == 3:  # send similarity and receive encrypted context
        similarities = pop_content("c2")

        top_k = 2
        indices = choose_indices(similarities=similarities, top_k=top_k)
        contexts = send_indices_and_receive_contexts(indices=indices)

        print(f"{contexts=}")
        set_content("c3", contexts)

        no_sync = pop_content("no_sync") or False
        set_content("no_sync", no_sync)

        return {"no_sync": no_sync}

    elif step == 4:
        no_sync = pop_content("no_sync") or False

        if no_sync:
            return {"answer": "복호화 키 검증에 실패했습니다. 키를 재설정해주세요."}

        # make RAG prompt, request generation, and... get answer
        contexts = pop_content("c3") or []

        answer = generate_answer(query=query, contexts=contexts)
        return {"answer": answer}

    return "OK"
