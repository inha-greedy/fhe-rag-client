import os
import zipfile

import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv
from Pyfhel import Pyfhel
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .enc import get_he_context, set_he_context


def save_public_key():
    he = get_he_context()
    zip_file_path = "./client/storage/public_keys.zip"

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())
    print(f"Public Keys saved to {zip_file_path}")


def save_all_key():
    he = get_he_context()
    zip_file_path = "./client/storage/keys.zip"

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())
        zipf.writestr("sec.key.bytes", he.to_bytes_secret_key())
    print(f"Public, Secret Keys saved to {zip_file_path}")


def _clear_storage() -> None:
    """
    저장소를 비웁니다.
    """
    storage_path = "./client/storage"

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


def save_key(contents: bytes) -> None:
    _clear_storage()

    key_path = "./client/storage/keys.zip"

    with open(key_path, "wb") as fp:
        fp.write(contents)


def load_all_key() -> None:
    he = Pyfhel()

    zip_file_path = "./client/storage/keys.zip"

    with zipfile.ZipFile(zip_file_path, "r") as zipf:
        with zipf.open("context.bytes") as f:
            he.from_bytes_context(f.read())
        with zipf.open("public_key.bytes") as f:
            he.from_bytes_public_key(f.read())
        with zipf.open("relin_key.bytes") as f:
            he.from_bytes_relin_key(f.read())
        with zipf.open("rotate_key.bytes") as f:
            he.from_bytes_rotate_key(f.read())
        with zipf.open("sec.key.bytes") as f:
            he.from_bytes_secret_key(f.read())

    set_he_context(he=he)
    print(f"Public, Secret Keys loaded from {zip_file_path}")


def send_public_key_to_server():
    zip_file_path = "./client/storage/public_keys.zip"

    with open(zip_file_path, "rb") as zip_file:
        load_dotenv()

        server_url = os.getenv("SERVER_URL")

        # FormData 생성
        form_data = MultipartEncoder(
            fields={"file": ("public_keys.zip", zip_file, "application/zip")}
        )

        # HTTP 요청 헤더 설정
        headers = {"Content-Type": form_data.content_type}

        response = requests.post(
            server_url + "/sync-key", data=form_data, headers=headers, timeout=9
        )

        return response
