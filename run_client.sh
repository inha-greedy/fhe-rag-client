#!/bin/bash

UVICORN_APP="client.main:app"
PORT=8000

# 브라우저 열기
open "http://localhost:$PORT"

# uvicorn 서버 실행
uvicorn "$UVICORN_APP" --port "$PORT" --reload