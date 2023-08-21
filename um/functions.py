import os
import uuid


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    return os.path.join(instance.UPLOAD_TO, f"{uuid.uuid4()}.{ext}")
