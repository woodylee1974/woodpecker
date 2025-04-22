from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Dict
import json
import time
import random
from utils.file_man import unzip_file
from utils.scaner import start_scan, get_scan_status, collect_files
from utils.ssf import find_exact_same_substrings


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 