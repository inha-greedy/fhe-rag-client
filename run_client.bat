@echo off

set UVICORN_APP=client.main:app
set PORT=8000

# 브라우저 열기
start http://localhost:%PORT%

# uvicorn 서버 실행
uvicorn %UVICORN_APP% --host 0.0.0.0 --port %PORT% --reload