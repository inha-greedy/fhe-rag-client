from fastapi import APIRouter, Form, UploadFile

from ..services.document import (
    embed_documents,
    encrypt_documents,
    read_file,
    send_documents,
    split_content,
)
from ..services.storage import set_content, pop_content

document_router = APIRouter()


@document_router.post("/document")
async def set_document(file: UploadFile = None, step: int = Form(...)):
    if step == 1:  # read document
        str_content, size = await read_file(file=file)
        set_content("s1", str_content)

        return {
            "file_size": size,
        }

    elif step == 2:  # parse document to make splitted_documents
        str_content = pop_content("s1")

        chunk_size = 300
        splitted_contents = split_content(str_content=str_content, chunk_size=chunk_size)
        set_content("s2", splitted_contents)

        return {"chunk_size": chunk_size, "num_documents": len(splitted_contents)}

    elif step == 3:  # embed each splitted_documents
        splitted_contents = pop_content("s2")
        documents, avg_time = embed_documents(documents=splitted_contents)
        set_content("s3", documents)

        return {"avg_embed_time": avg_time}

    elif step == 4:  # encrypt documents
        documents = pop_content("s3")
        encrypted_documents, avg_time = encrypt_documents(documents=documents)
        set_content("s4", encrypted_documents)

        return {"avg_encrypt_time": avg_time}

    elif step == 5:  # send List[PyCDocument] to storage-server
        encrypted_documents = pop_content("s4")
        response = send_documents(
            uri="/upload-docs",
            encrypted_documents=encrypted_documents,
        ).json()

        return response

    return "NO"
