import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

example_router = APIRouter()


@example_router.get("/example")
async def download_example():
    melon_content = os.path.join("client", "templates", "assets", "melon-top-100.txt")
    try:
        headers = {"Content-Disposition": 'attachment; filename="melon-top-100.txt"'}
        return FileResponse(melon_content, headers=headers)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail="File not found") from e
