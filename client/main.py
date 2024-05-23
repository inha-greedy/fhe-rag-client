from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from .routes.chat import chat_router
from .routes.document import document_router
from .routes.key import key_router
from .routes.example import example_router
from .services.session import set_user_id

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
app.include_router(chat_router)
app.include_router(document_router)
app.include_router(key_router)
app.include_router(example_router)

# HTML 파일 로드
with open(BASE_DIR / "templates" / "index.html", "r", encoding="utf-8") as f:
    html_content = f.read()


@app.middleware("http")
async def add_user_id_to_request(request: Request, call_next):
    """
    모든 요청에 대해 사용자 ID를 추가합니다.
    """
    set_user_id(request=request)
    response = await call_next(request)
    return response


@app.get("/", response_class=HTMLResponse)
async def html_template():
    """
    관제 페이지를 띄웁니다.
    """
    return HTMLResponse(content=html_content, status_code=200)
