import os
from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import FileResponse

from ..services.storage import save_zipfile, save_public_key, save_all_key
from ..services.key import (
    load_he_from_key,
    send_public_key_to_server,
    setup_ckks_context,
    get_all_key_path,
)

key_router = APIRouter()


@key_router.post("/key")
async def set_encryption_key(file: UploadFile = None, step: int = Form(...)):
    if step == 1:
        if file is not None:
            contents = await file.read()
            key_name = file.filename
            save_zipfile(contents=contents)
            he = load_he_from_key()
            save_all_key(he=he)
            save_public_key(he=he)
            return {"key_name": key_name}

        else:
            he = setup_ckks_context()
            save_all_key(he=he)
            save_public_key(he=he)

    elif step == 2:
        # 2. public file -> storage-server
        send_public_key_to_server()

    return "OK"


@key_router.get("/key")
async def get_key():
    key_path = get_all_key_path()
    print(f"{key_path=}")
    if os.path.exists(key_path):
        return FileResponse(key_path, media_type="application/zip", filename="key.zip")
    return {"error": "File not found"}
