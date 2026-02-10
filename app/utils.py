import os
from datetime import datetime

UPLOAD_DIR = "uploads"

def save_file(contents: bytes, filename: str) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Make filename unique
    unique_name = f"{int(datetime.utcnow().timestamp())}_{filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    return file_path
