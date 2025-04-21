import zipfile
import glob
import os
import shutil
from io import BytesIO

UPLOAD_DIR = "uploads"

def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.unlink(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)


def unzip_file(zip_file_bytes, dest_path):
    extracted_files = []
    with BytesIO(zip_file_bytes) as zip_stream:
        with zipfile.ZipFile(zip_stream) as zip_file:
            zip_contents = zip_file.namelist()
            zip_file.extractall(path=dest_path)

            for item in zip_contents:
                full_path = os.path.join(dest_path, item)
                if not item.endswith('/'):
                    extracted_files.append(full_path)


def collect_pdf_files():
    pdf_files = []
    for root, dirs, files in os.walk(UPLOAD_DIR):
        for file in files:
            if file.lower().endswith('.pdf'):
                full_path = os.path.join(root, file)
                scaned_path = full_path.replace(".pdf", ".pdf.json")
                pdf_files.append((full_path, scaned_path))
    return pdf_files