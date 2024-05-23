"""
세션 설정에 사용되는 비즈니스 로직을 담은 코드 페이지입니다.
"""

import hashlib
from typing import Any, Dict
from fastapi import Request

_user_map: Dict[str, str] = {"user_id": "qqqq"}
_content_map: Dict[str, Any] = {}


def _string_to_hash(string, length=16):
    hash_obj = hashlib.sha256(string.encode("utf-8"))
    hex_dig = hash_obj.hexdigest()
    return hex_dig[:length]


def set_content(name: str, content):
    user_id = get_user_id()
    map_name = user_id + "_" + name
    _content_map[map_name] = content


def pop_content(name: str) -> Any:
    user_id = get_user_id()
    map_name = user_id + "_" + name

    try:
        return _content_map.pop(map_name)

    except KeyError:
        return None


def get_user_id() -> str:
    """
    get user_id
    """
    return _user_map.get("user_id") or "EMPTY"


def set_user_id(request: Request):
    """
    set user_id
    """
    host = request.headers.get("host")
    agent = request.headers.get("user-agent")
    user_key = f"host:{host}::agent:{agent}"

    _user_map["user_id"] = _string_to_hash(user_key)
