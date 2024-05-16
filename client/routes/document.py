from fastapi import APIRouter, Form, UploadFile


from ..services.document import (
    read_file,
    split_content,
    embed_documents,
    encrypt_documents,
    send_documents_to_server,
)

from ..services.storage import set_content, get_content

document_router = APIRouter()


@document_router.post("/document")
async def set_document(file: UploadFile = None, step: int = Form(...)):

    if step == 1:  # read document

        str_content = await read_file(file=file)
        set_content("s1", str_content)

    elif step == 2:  # parse document to make splitted_documents

        str_content = get_content("s1")
        splitted_contents = split_content(str_content=str_content)
        set_content("s2", splitted_contents)

    elif step == 3:  # embed each splitted_documents

        # str_content = await read_file(file=file)
        # splitted_contents = split_content(str_content=str_content)
        # set_content("s2", splitted_contents)

        ###############
        splitted_contents = get_content("s2")
        documents = embed_documents(documents=splitted_contents)
        set_content("s3", documents)

    elif step == 4:  # encrypt documents

        # str_content = await read_file(file=file)
        # splitted_contents = split_content(str_content=str_content)
        # documents = embed_documents(documents=splitted_contents)
        # set_content("s3", documents)
        ###############

        documents = get_content("s3")
        encrypted_documents = encrypt_documents(documents=documents)
        set_content("s4", encrypted_documents)

    elif step == 5:  # send List[PyCDocument] to storage-server

        # str_content = await read_file(file=file)
        # splitted_contents = split_content(str_content=str_content)
        # documents = embed_documents(documents=splitted_contents)
        # encrypted_documents = encrypt_documents(documents=documents)
        # set_content("s4", encrypted_documents)
        ###############

        encrypted_documents = get_content("s4")
        response = send_documents_to_server(
            uri="/enc-docs", encrypted_documents=encrypted_documents
        ).json()

        return response

    return "OK"
