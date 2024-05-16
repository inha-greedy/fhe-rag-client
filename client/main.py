from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routes.chat import chat_router
from .routes.document import document_router
from .routes.key import key_router
from .services.enc import set_he_context

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# 정적 파일 디렉터리 설정
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(key_router)


# set default HE Key
set_he_context()

# HTML 파일 로드
with open(BASE_DIR / "templates" / "index.html", "r", encoding="utf-8") as f:
    html_content = f.read()


@app.get("/", response_class=HTMLResponse)
async def html_template():
    """
    관제 페이지를 띄웁니다.
    """
    return HTMLResponse(content=html_content, status_code=200)
