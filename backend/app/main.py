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


@app.post("/backend/compare")
async def compare_files():
    # This is a placeholder for your comparison algorithm
    # You'll need to implement the actual comparison logic
    extracted_dir = UPLOAD_DIR / "extracted"
    if not extracted_dir.exists():
        return {"error": "No files to compare"}
    
    # Placeholder for comparison results
    results = {
        "similar_segments": []
    }
    
    return results


@app.get("/backend/file-status")
async def get_file_status():
    data = {
        'files': [
        {
            'name': "file1",
            "status": {'state':"pending", 'message': "waiting"},
            "progress": 10
        },
        {
            'name': "file1",
            "status": {'state': "pending", 'message': "waiting"},
            "progress": 10
        },
        {
            'name': "file1",
            "status": {'state': "pending", 'message': "waiting"},
            "progress": 10
        },
        {
            'name': "file1",
            "status": {'state': "pending", 'message': "waiting"},
            "progress": 10
        }
    ],
       'all_indexed': False
    }

    return JSONResponse(
            content= data,
            status_code=200
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 