import os
import zipfile

from Pyfhel import Pyfhel

from .session import get_user_id


def save_public_key(he: Pyfhel) -> None:
    zip_file_path = get_public_key_path()

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())


def save_all_key(he: Pyfhel) -> None:
    zip_file_path = get_all_key_path()

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())
        zipf.writestr("sec.key.bytes", he.to_bytes_secret_key())


def exists_all_key() -> bool:
    key_path = get_all_key_path()
    return os.path.exists(key_path)


def exists_public_key() -> bool:
    key_path = get_public_key_path()
    return os.path.exists(key_path)


def save_zipfile(contents: bytes) -> None:
    _clear_storage()

    zip_file_path = get_all_key_path()

    with open(zip_file_path, "wb") as fp:
        fp.write(contents)


def _clear_storage() -> None:
    """
    저장소를 비웁니다.
    """
    storage_path = _get_storage_path()

    # 기존 디렉토리 및 하위 내용 삭제
    if os.path.exists(storage_path):
        for root, dirs, files in os.walk(storage_path, topdown=False):
            for file_name in files:
                os.remove(os.path.join(root, file_name))
            for dir_name in dirs:
                os.rmdir(os.path.join(root, dir_name))
        os.rmdir(storage_path)

    #  디렉토리 재생성
    os.makedirs(storage_path)


def _get_storage_path() -> str:
    user_id = get_user_id()
    storage_path = os.path.join("client", "storage", str(user_id))
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    return storage_path


def get_public_key_path() -> str:
    storage_path = _get_storage_path()
    return os.path.join(storage_path, "public_key.zip")


def get_all_key_path() -> str:
    storage_path = _get_storage_path()
    return os.path.join(storage_path, "key.zip")
