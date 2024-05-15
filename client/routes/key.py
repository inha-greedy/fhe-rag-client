from fastapi import APIRouter

from ..services.enc import set_he_context

key_router = APIRouter()


@key_router.post("/key")
async def set_encryption_key():

    # TODO: set KEY on process
    set_he_context()

    return "OK"
