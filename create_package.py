"""
SupportPilot — Project Packager
Creates a clean distributable ZIP excluding venv, node_modules,
__pycache__, .git, build artifacts, etc.
"""

import os
import zipfile
from pathlib import Path

BASE_DIR = Path(r"c:\Users\Theja\Downloads\files")
OUTPUT_ZIP = BASE_DIR / "SupportPilot_Final.zip"

# Folders/files to include (relative to BASE_DIR)
INCLUDE_DIRS = [
    "rag_module",
    "kb_milestone3",
    "ticket-app",
]
INCLUDE_FILES = [
    "README.md",
    "db.json",
]

# Patterns to EXCLUDE from any folder
EXCLUDE_DIRS = {
    "venv", "node_modules", "__pycache__", ".git",
    ".venv", "dist", "build", ".next", "chroma_db",
    ".cache", "coverage", ".pytest_cache",
}
EXCLUDE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".egg-info",
    ".log", ".DS_Store",
}
EXCLUDE_FILES = {
    ".env",                   # contains secrets
    "integrations_config.json",  # contains secrets (email/jira creds)
}

def should_exclude(path: Path) -> bool:
    # Exclude by directory name
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    # Exclude by file extension
    if path.suffix in EXCLUDE_EXTS:
        return True
    # Exclude specific filenames
    if path.name in EXCLUDE_FILES:
        return True
    return False

count = 0
total_size = 0

print(f"Creating: {OUTPUT_ZIP}\n")

with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:

    # Add individual root files
    for fname in INCLUDE_FILES:
        fpath = BASE_DIR / fname
        if fpath.exists():
            arcname = f"SupportPilot/{fname}"
            zf.write(fpath, arcname)
            print(f"  + {arcname}")
            count += 1

    # Add each directory recursively
    for folder in INCLUDE_DIRS:
        folder_path = BASE_DIR / folder
        if not folder_path.exists():
            print(f"  [SKIP] {folder} — not found")
            continue

        for file_path in folder_path.rglob("*"):
            if not file_path.is_file():
                continue

            rel = file_path.relative_to(BASE_DIR)
            if should_exclude(rel):
                continue

            arcname = f"SupportPilot/{rel}"
            zf.write(file_path, arcname)
            size = file_path.stat().st_size
            total_size += size
            count += 1

    # -------------------------------------------------------
    # Add a teammate-friendly README
    # -------------------------------------------------------
    teammate_readme = """# SupportPilot — Setup Guide for Teammates

## Prerequisites
Install these before you start:
- Python 3.10+  (https://www.python.org/downloads/)
- Node.js 18+   (https://nodejs.org/)
- MySQL 8.0+    (https://dev.mysql.com/downloads/)
- Git (optional)

---

## Step 1 — Set up the MySQL Database

1. Open MySQL Workbench or MySQL CLI
2. Create a database:
   ```sql
   CREATE DATABASE supportpilot;
   ```
3. Open `rag_module/.env` and fill in your MySQL credentials:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=supportpilot
   ```
4. The tables are auto-created when the RAG backend starts.

---

## Step 2 — Set up the RAG Backend (Port 8000)

```bash
cd rag_module
python -m venv venv

# Windows:
venv\\Scripts\\activate

pip install -r requirements.txt
```

Edit `.env` and add your **Groq API key**:
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key at: https://console.groq.com

---

## Step 3 — Set up the Knowledge Base API (Port 8001)

```bash
cd kb_milestone3\\kb_m3
python -m venv venv

# Windows:
venv\\Scripts\\activate

pip install -r requirements.txt
```

---

## Step 4 — Set up the React Frontend (Port 5173)

```bash
cd ticket-app
npm install
```

---

## Step 5 — Run Everything

Double-click `run_all.bat` — it starts all 3 services automatically.

Or start manually in 3 separate terminals:
```bash
# Terminal 1 — KB API
cd kb_milestone3\\kb_m3
venv\\Scripts\\python.exe -m uvicorn api:app --port 8001

# Terminal 2 — RAG Backend
cd rag_module
venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000

# Terminal 3 — Frontend
cd ticket-app
npm run dev
```

---

## Step 6 — Configure Integrations (Optional)

Open the app at http://localhost:5173 → Go to **Integrations**

- **Email:** Add a Gmail address + App Password (Google Account → Security → App Passwords)
- **Jira:** Add your Atlassian URL, email, API token, and project key

---

## URLs
| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| RAG API | http://localhost:8000 |
| KB API | http://localhost:8001 |
| API Docs | http://localhost:8000/docs |

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` inside the correct folder |
| `npm: command not found` | Install Node.js from https://nodejs.org |
| DB connection error | Check `.env` MySQL credentials |
| Groq 429 rate limit | Daily token limit hit — wait until midnight or upgrade plan |
| Port already in use | Kill the process using that port and restart |
"""
    zf.writestr("SupportPilot/SETUP_README.md", teammate_readme)
    print("  + SupportPilot/SETUP_README.md  [generated]")

    # -------------------------------------------------------
    # Add a fixed run_all.bat that works on any machine
    # (removes hardcoded Python path)
    # -------------------------------------------------------
    portable_bat = """@echo off
echo ===================================================
echo  SupportPilot - Starting All Services
echo ===================================================
echo.

:: 1. Knowledge Base API on Port 8001
echo [1/3] Starting Knowledge Base API (Port 8001)...
start "KB API - Port 8001" cmd /k "cd kb_milestone3\\kb_m3 && venv\\Scripts\\python.exe -m uvicorn api:app --port 8001 --host 127.0.0.1"
timeout /t 3 /nobreak >nul

:: 2. RAG Backend on Port 8000
echo [2/3] Starting RAG Backend (Port 8000)...
start "RAG Backend - Port 8000" cmd /k "cd rag_module && venv\\Scripts\\python.exe -m uvicorn app.main:app --port 8000 --host 127.0.0.1"
timeout /t 5 /nobreak >nul

:: 3. React Frontend on Port 5173
echo [3/3] Starting React Frontend (Port 5173)...
start "Frontend - Port 5173" cmd /k "cd ticket-app && npm run dev"

echo.
echo ===================================================
echo  All services launched in separate windows.
echo  Frontend  : http://localhost:5173
echo  RAG API   : http://localhost:8000
echo  KB API    : http://localhost:8001
echo  API Docs  : http://localhost:8000/docs
echo ===================================================
echo.
echo  NOTE: Wait ~15 seconds for all services to fully start.
echo  Press any key to close this window.
pause
"""
    zf.writestr("SupportPilot/run_all.bat", portable_bat)
    print("  + SupportPilot/run_all.bat  [portable version generated]")

zip_size_mb = OUTPUT_ZIP.stat().st_size / (1024 * 1024)
print(f"\n{'='*50}")
print(f"  Files packed : {count}")
print(f"  Source size  : {total_size / (1024*1024):.1f} MB")
print(f"  ZIP size     : {zip_size_mb:.1f} MB")
print(f"  Output       : {OUTPUT_ZIP}")
print(f"{'='*50}")
