# Text Comparison Tool

A web application for comparing text files within a ZIP archive. Built with Svelte and FastAPI.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   └── main.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── App.svelte
    │   ├── app.css
    │   └── main.js
    ├── index.html
    ├── package.json
    ├── postcss.config.js
    ├── tailwind.config.js
    └── vite.config.js
```

## Setup and Running

### Backend

1. Create a virtual environment and activate it:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
cd app
uvicorn main:app --reload
```

The backend will be available at http://localhost:8000

### Frontend

1. Install Node.js dependencies:
```bash
cd frontend
npm install
```

2. Run the development server:
```bash
npm run dev
```

The frontend will be available at http://localhost:5173

## Features

- Upload ZIP files containing text files
- Extract and process uploaded files
- Compare text content between files
- Clean up uploaded files
- Modern UI with Tailwind CSS

## Note

The text comparison algorithm implementation is left for you to implement in the backend's `compare_files` function in `main.py`. 