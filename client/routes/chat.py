from fastapi import APIRouter, Form


from ..services.chat import send_query_and_receive_encrypted_top_k

chat_router = APIRouter()


@chat_router.post("/chat")
async def chat(query: str = Form(...)):

    # TODO: send embed query to storage-server, and... receive encrypted top-k list
    send_query_and_receive_encrypted_top_k(query)

    # TODO: **decrypt** top-k list

    # TODO: send decrypted top-k list, and... receive top-k document

    # TODO: make RAG prompt using top-k document

    # TODO: request generation to llm-server
    # TODO: and... get answer

    return "OK"
