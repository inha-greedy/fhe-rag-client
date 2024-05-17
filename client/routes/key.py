from fastapi import APIRouter, UploadFile, Form


from ..services.enc import set_he_context
from ..services.key import (
    save_key,
    save_public_key,
    load_all_key,
    send_public_key_to_server,
)

key_router = APIRouter()


@key_router.post("/key")
async def set_encryption_key(file: UploadFile = None, is_new: int = Form(...)):

    if is_new == 0:
        # 1. byte -> file
        contents = await file.read()
        save_key(contents=contents)

        # 2. file -> HE (on memory)
        load_all_key()
    else:
        set_he_context()

    # 3. HE -> public file
    save_public_key()

    # 4. public file -> storage-server
    send_public_key_to_server()

    return "OK"
