from fastapi import APIRouter, UploadFile, Form

from ..services.storage import (
    save_zipfile,
    save_public_key,
    save_all_key,
    exists_all_key,
    exists_public_key,
)
from ..services.key import load_he_from_key, send_public_key_to_server, setup_ckks_context

key_router = APIRouter()


@key_router.post("/key")
async def set_encryption_key(file: UploadFile = None, step: int = Form(...)):
    if step == 1:
        if file is not None:
            contents = await file.read()
            save_zipfile(contents=contents)
            he = load_he_from_key()
            save_public_key(he=he)

        elif not exists_all_key():
            he = setup_ckks_context()
            save_all_key(he=he)
            save_public_key(he=he)

        elif not exists_public_key():
            he = load_he_from_key()
            save_public_key(he=he)

    elif step == 2:
        # 2. public file -> storage-server
        send_public_key_to_server()

    return "OK"
