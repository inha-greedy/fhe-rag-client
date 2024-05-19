import os
import zipfile
import base64
import numpy as np
from Pyfhel import PyCtxt, Pyfhel
import requests  # type: ignore # noqa: F401
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder

from .storage import get_all_key_path, get_public_key_path


def load_he_from_key() -> Pyfhel:
    he = Pyfhel()

    zip_file_path = get_all_key_path()

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

    return he


def setup_ckks_context(scale: int = 2**30) -> Pyfhel:
    he = Pyfhel()
    ckks_params = {
        "scheme": "CKKS",
        "n": 2**13,
        "scale": scale,
        "qi_sizes": [21] * 5,
    }
    he.contextGen(**ckks_params)
    he.keyGen()
    he.relinKeyGen()
    he.rotateKeyGen()

    return he


def send_public_key_to_server():
    zip_file_path = get_public_key_path()

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


def encrypt_document(document: str) -> PyCtxt:
    emb = _string_to_numpy(document)

    return encrypt_ndarray(emb)


def encrypt_ndarray(ndarr: np.ndarray) -> PyCtxt:
    he = load_he_from_key()

    n_slots = he.get_nSlots()
    ctxt = [he.encrypt(ndarr[j : j + n_slots]) for j in range(0, len(ndarr), n_slots)]

    return ctxt[0]


def ctxt_to_str(ctxt: PyCtxt) -> str:
    return base64.b64encode(ctxt.to_bytes()).decode("utf-8")


def _string_to_numpy(str_to_convert: str) -> np.ndarray:
    arr_str = np.array([ord(c) for c in str_to_convert], dtype=np.float64)

    return arr_str
