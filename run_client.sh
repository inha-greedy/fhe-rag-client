#!/bin/bash

UVICORN_APP="client.main:app"
PORT=8000

# 브라우저 열기
open "http://0.0.0.0:$PORT"

# uvicorn 서버 실행
uvicorn "$UVICORN_APP" --host 0.0.0.0 --port "$PORT" --reload