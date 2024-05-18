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
    if step == 1:
        # send embed query to storage-server, and... receive encrypted similarity

        encrypted_similarities = get_similarities_from_server(query=query)

        print(f"{encrypted_similarities=}")
        set_content("c1", encrypted_similarities)

    elif step == 2:
        encrypted_similarities = pop_content("c1")

        # decrypt similarity
        similarities = decrypt_similarities(encrypted_similarities=encrypted_similarities)

        print(f"{similarities=}")
        set_content("c2", similarities)

    elif step == 3:
        similarities = pop_content("c2")

        # send similarity, and... receive encrypted context
        num_context = 2
        indices = choose_indices(similarities=similarities, num_context=num_context)
        contexts = send_indices_and_receive_contexts(indices=indices)

        print(f"{contexts=}")
        set_content("c3", contexts)

    elif step == 4:
        # make RAG prompt, request generation, and... get answer
        contexts = pop_content("c3") or []
        answer = generate_answer(query=query, contexts=contexts)

        return {"answer": answer}

    return "OK"
