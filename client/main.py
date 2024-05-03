from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent

# 정적 파일 디렉터리 설정
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# HTML 파일 로드
with open(BASE_DIR / "templates" / "index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

@app.get("/", response_class=HTMLResponse)
async def html_template():
    """
    관제 페이지를 띄웁니다.
    """
    return HTMLResponse(content=html_content, status_code=200)
