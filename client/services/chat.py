from ..services.document import (
    split_content,
    embed_documents,
    encrypt_documents,
    send_documents_to_server,
)


def send_query_and_receive_encrypted_top_k(query: str):

    splitted_documents = split_content(str_content=query)

    documents = embed_documents(documents=splitted_documents)

    encrypted_documents = encrypt_documents(documents=documents)

    response = send_documents_to_server(
        uri="/emb-query",
        encrypted_documents=encrypted_documents,
    )

    received_top_k = response

    return received_top_k
