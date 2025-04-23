from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
from pathlib import Path
from typing import List
from utils.file_man import unzip_file
from utils.scaner import start_scan, get_scan_status, collect_files
from utils.ssf import find_exact_same_substrings
from utils.pdf_show import render_image
from pydantic import BaseModel
import base64

app = FastAPI()

origins = ["*"]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/backend/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.zip'):
        return {"error": "Only ZIP files are allowed"}
    
    file_bytes = await file.read()
    unzip_file(file_bytes, UPLOAD_DIR)
    
    return {"message": "File uploaded and extracted successfully"}


@app.post("/backend/cleanup")
async def cleanup():
    if UPLOAD_DIR.exists():
        shutil.rmtree(UPLOAD_DIR)
    return {"message": "Upload directory cleaned successfully"}


@app.post("/backend/scan")
async def scan_files():
    collect_files()
    start_scan()
    return {"message": "成功启动扫描..."}


@app.get("/backend/compare")
async def compare_files():
    results = find_exact_same_substrings()
    return results


@app.get("/backend/file-status")
async def get_file_status():
    data = get_scan_status()
    return JSONResponse(
            content= data,
            status_code=200
        )

@app.get("/backend/collect-info")
async def get_file_status():
    collect_files()
    data = get_scan_status()
    return JSONResponse(
            content=data,
            status_code=200
        )


class PdfInfo(BaseModel):
    file: str
    block: dict


@app.post("/backend/get_pdf_pair")
async def get_pdf_pair(pdf_pair: List[PdfInfo]):
    images = []
    for pdf in pdf_pair:
        from_file = pdf.file
        bbox = pdf.block['bbox']
        page = pdf.block['page']
        page_boxes = [(page, bbox)]
        offset = 0
        image = render_image(from_file, page_boxes, offset)
        images.append(base64.b64encode(image).decode('utf-8'))
    return {
        "left_image": images[0],
        "right_image": images[1],
        "message": "Successfully retrieved PDF images."
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 