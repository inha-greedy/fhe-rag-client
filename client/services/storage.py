import os
import zipfile
from PIL import Image

from Pyfhel import Pyfhel

from .session import get_user_id


def save_public_key(he: Pyfhel) -> None:
    zip_file_path = get_public_key_path()
    image_path = get_image_path()

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())

    input_data = he.to_bytes_public_key()[1500:1506]

    # 고유 프랙탈 이미지 생성
    image = create_fractal_image(input_data)
    image.save(image_path)


def create_fractal_image(input_data, width: int = 800, height: int = 800):
    """
    Create a fractal image based on input data and save it to a file.

    Parameters
    ----------

    input_data : bytes or int or str
        Data used to generate fractal parameters.
        Can be bytes, an integer, or a bit-string (str).
    width : int
        Width of the image in pixels (default is 800).
    height : int
        Height of the image in pixels (default is 800).


    Returns
    -------
    image : :py:class:`~PIL.Image.Image`
        A fractal image
    """

    if isinstance(input_data, bytes):  # bytes
        input_data = input_data[:48]
        bits = "".join(format(byte, "08b") for byte in input_data)

        if len(bits) < 48:
            raise ValueError("length of bits must be up to 48.")

    elif isinstance(input_data, int):  # bit
        bits = format(input_data, "048b")

    elif isinstance(input_data, str):  # bit-string
        bits = input_data[:48]

        if len(bits) < 48:
            raise ValueError("length of bits must be up to 48.")

    else:
        raise TypeError("input_data must be in [ bytes, int, str(bit-string) ].")

    # set RGB color
    r = int(bits[:8], 2) % 256
    g = int(bits[8:16], 2) % 256
    b = int(bits[16:24], 2) % 256

    # set fractal parameters
    max_iterations = int(bits[24:32], 2) % 100 + 50
    bailout = int(bits[32:40], 2) / 256.0 + 2.0
    power = int(bits[40:48], 2) / 16.0 + 1.0

    # set image size
    fractal_image = Image.new("RGB", (width, height))

    # generate fractal art
    for x in range(width):
        for y in range(height):
            cx = (x - width / 2) / (width / 4.0)
            cy = (y - height / 2) / (height / 4.0)

            c = complex(cx, cy)
            z = 0j

            for i in range(max_iterations):
                z = z**power + c
                if abs(z) > bailout:
                    break

            color = (r * i % 256, g * i % 256, b * i % 256)
            fractal_image.putpixel((x, y), color)

    return fractal_image


def save_all_key(he: Pyfhel) -> None:
    zip_file_path = get_all_key_path()

    with zipfile.ZipFile(zip_file_path, "w") as zipf:
        zipf.writestr("context.bytes", he.to_bytes_context())
        zipf.writestr("public_key.bytes", he.to_bytes_public_key())
        zipf.writestr("relin_key.bytes", he.to_bytes_relin_key())
        zipf.writestr("rotate_key.bytes", he.to_bytes_rotate_key())
        zipf.writestr("sec.key.bytes", he.to_bytes_secret_key())

    print(f"key saved: {zip_file_path}")


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
    storage_path = os.path.join("client", "storage", user_id)
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    return storage_path


def get_public_key_path() -> str:
    storage_path = _get_storage_path()
    return os.path.join(storage_path, "public_key.zip")


def get_all_key_path() -> str:
    storage_path = _get_storage_path()
    return os.path.join(storage_path, "key.zip")


def get_image_path() -> str:
    storage_path = _get_storage_path()
    return os.path.join(storage_path, "image.png")
