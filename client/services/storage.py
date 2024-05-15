STORAGE = {}


def set_content(name: str, content):

    STORAGE[name] = content

    # print(f"{STORAGE=}")


def get_content(name: str) -> any:

    return STORAGE[name]
