from typing import Any

STORAGE = {}


def set_content(name: str, content):
    STORAGE[name] = content

    # print(f"{STORAGE=}")


def get_content(name: str) -> Any:
    try:
        return STORAGE[name]

    except KeyError as e:
        print(f"Content KeyError :: {e=}")

        return None


def pop_content(name: str) -> Any:
    try:
        return STORAGE.pop(name)

    except KeyError as e:
        print(f"Content KeyError :: {e=}")

        return None
