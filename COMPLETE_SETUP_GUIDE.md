# COMPLETE SETUP GUIDE - AI Research Assistant
# For GitHub Copilot / AI Assistants / Step-by-Step Instructions

## CRITICAL REQUIREMENTS
- Python Version: 3.12.x (NOT 3.14, NOT 3.13, NOT 3.11 or lower)
- OS: Windows, macOS, or Linux
- Disk Space: 1GB free
- RAM: 4GB minimum

---

## PHASE 1: VERIFY PYTHON VERSION

### Step 1.1: Check Current Python Version
```bash
python --version
```

Expected output: `Python 3.12.x` (where x is any number)

If you see `Python 3.14.x` or `Python 3.13.x` - YOU MUST INSTALL PYTHON 3.12

### Step 1.2: If Wrong Version - Download Python 3.12.8
1. Go to: https://www.python.org/downloads/release/python-3128/
2. Download the installer for your OS:
   - Windows: "Windows installer (64-bit)"
   - macOS: "macOS 64-bit universal2 installer"
   - Linux: Use package manager (see below)

### Step 1.3: Install Python 3.12.8

**WINDOWS:**
1. Run the downloaded .exe file
2. ✅ CHECK "Add Python 3.12 to PATH" (CRITICAL!)
3. Click "Install Now"
4. Wait for installation to complete
5. Open NEW command prompt (close old ones)
6. Verify: `py -3.12 --version` should show "Python 3.12.8"

**macOS:**
1. Run the downloaded .pkg file
2. Follow installation wizard
3. Open NEW terminal (close old ones)
4. Verify: `python3.12 --version` should show "Python 3.12.8"

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev
python3.12 --version
```

---

## PHASE 2: EXTRACT PROJECT FILES

### Step 2.1: Download Project
- Download `research-assistant.zip` (Windows) or `research-assistant.tar.gz` (Mac/Linux)
- Save to a known location (e.g., `C:\Users\YourName\Documents\`)

### Step 2.2: Extract Files

**WINDOWS:**
1. Right-click `research-assistant.zip`
2. Select "Extract All..."
3. Choose destination folder (e.g., `C:\Users\YourName\Documents\`)
4. Click "Extract"

**macOS:**
1. Double-click `research-assistant.tar.gz` (auto-extracts)
2. Or in terminal: `tar -xzf research-assistant.tar.gz`

**Linux:**
```bash
tar -xzf research-assistant.tar.gz
cd research-assistant
```

### Step 2.3: Verify Files Exist
You should see these files/folders:
```
research-assistant/
├── app/
├── tests/
├── requirements.txt
├── README.md
├── SETUP.md
└── quick_start.py
```

---

## PHASE 3: OPEN PROJECT IN VS CODE

### Step 3.1: Open VS Code
1. Launch Visual Studio Code

### Step 3.2: Open Project Folder
1. Click "File" → "Open Folder"
2. Navigate to the `research-assistant` folder you extracted
3. Click "Select Folder"

### Step 3.3: Open Integrated Terminal
1. In VS Code, press: `Ctrl+` ` (backtick key) or `View → Terminal`
2. You should see a terminal panel at the bottom

---

## PHASE 4: CREATE VIRTUAL ENVIRONMENT WITH PYTHON 3.12

**CRITICAL: We must use Python 3.12 specifically**

### Step 4.1: Navigate to Project (if not already there)
```bash
# Check you're in the right folder
# Windows:
dir
# macOS/Linux:
ls

# You should see: app/, tests/, requirements.txt, etc.
```

### Step 4.2: Create Virtual Environment

**WINDOWS (if you have Python 3.12):**
```bash
py -3.12 -m venv venv
```

**WINDOWS (alternative if above doesn't work):**
```bash
python -m venv venv
```

**macOS/Linux:**
```bash
python3.12 -m venv venv
```

Expected output: Creates a `venv/` folder (takes 10-30 seconds)

### Step 4.3: Activate Virtual Environment

**WINDOWS (Command Prompt):**
```bash
venv\Scripts\activate
```

**WINDOWS (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Expected Result:** Your prompt should now show `(venv)` at the start:
```
(venv) C:\Users\YourName\Documents\research-assistant>
```

### Step 4.4: Verify Python Version Inside Virtual Environment
```bash
python --version
```

**MUST show: Python 3.12.x**

If it shows 3.14 or anything else - DELETE venv folder and recreate:
```bash
# Deactivate first
deactivate

# Delete venv folder
# Windows:
rmdir /s venv
# macOS/Linux:
rm -rf venv

# Try again with explicit Python 3.12 path
```

---

## PHASE 5: SELECT PYTHON INTERPRETER IN VS CODE

### Step 5.1: Open Command Palette
- Press: `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)

### Step 5.2: Select Interpreter
1. Type: "Python: Select Interpreter"
2. Press Enter
3. Choose the one that shows: `./venv/bin/python` or `.\venv\Scripts\python.exe`
4. It should say "Python 3.12.x"

---

## PHASE 6: INSTALL DEPENDENCIES

**IMPORTANT: Make sure (venv) is active in your terminal!**

### Step 6.1: Upgrade pip
```bash
python -m pip install --upgrade pip
```

Expected output: "Successfully installed pip-24.x.x"

### Step 6.2: Install All Packages
```bash
pip install -r requirements.txt
```

**This will take 3-5 minutes. You'll see:**
- Downloading packages
- Installing: fastapi, uvicorn, sentence-transformers, torch, chromadb, etc.

**Expected final output:**
```
Successfully installed fastapi-0.109.0 uvicorn-0.27.0 torch-2.1.2 ... (many packages)
```

### Step 6.3: Download NLTK Data
```bash
python -c "import nltk; nltk.download('punkt')"
```

Expected output:
```
[nltk_data] Downloading package punkt to ...
[nltk_data]   Unzipping tokenizers/punkt.zip.
```

### Step 6.4: Verify Installation
```bash
pip list
```

You should see a long list including:
- fastapi
- uvicorn
- sentence-transformers
- torch
- chromadb
- pydantic

---

## PHASE 7: CONFIGURE ENVIRONMENT (Optional)

### Step 7.1: Copy Environment File
```bash
# Windows:
copy .env.example .env

# macOS/Linux:
cp .env.example .env
```

**Note:** The default settings work fine. You can skip editing this.

---

## PHASE 8: START THE SERVER

### Step 8.1: Run Uvicorn
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8.2: Expected Output
You should see:
```
INFO:     Will watch for changes in these directories: ['/path/to/research-assistant']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.

========================================
Starting AI Research Assistant v1.0.0
========================================
Loading embedding model...
✓ Embedding model loaded successfully
Connecting to vector database...
✓ Vector database connected: {...}
========================================
Application ready to receive requests
API: http://0.0.0.0:8000
Docs: http://0.0.0.0:8000/docs
========================================

INFO:     Application startup complete.
```

**FIRST RUN NOTE:** The first time you run this, it will download the embedding model (~90MB). This takes 1-3 minutes depending on your internet. Subsequent runs are instant.

### Step 8.3: Verify Server is Running
Open browser and go to: http://localhost:8000/docs

You should see the interactive API documentation (Swagger UI).

**LEAVE THIS TERMINAL RUNNING** - Don't close it!

---

## PHASE 9: TEST THE SYSTEM

### Step 9.1: Open New Terminal in VS Code
1. Click the "+" icon in the terminal panel (or `Ctrl+Shift+` `)
2. A second terminal opens
3. Activate venv again in this new terminal:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Step 9.2: Run Test Script
```bash
python quick_start.py
```

### Step 9.3: Expected Output
```
======================================================================
AI RESEARCH ASSISTANT - QUICK START TEST
======================================================================
✓ Server is running
  Status: {...}

======================================================================
INGESTING SAMPLE DOCUMENTS
======================================================================

Ingesting: ai_overview.txt
  ✓ Success
    Document ID: 20250131_120000_ai_overview_abc123de
    Chunks created: 5
    Embedding dimension: 384

[... more documents ...]

======================================================================
RUNNING TEST QUERIES
======================================================================

Query: What are the main applications of artificial intelligence?
----------------------------------------------------------------------
Results: 3 chunks found
Processing time: 45.23ms

Summary:
AI applications include autonomous vehicles, medical diagnosis, financial trading,
and virtual assistants. Machine learning enables computers to learn from data
without explicit programming.

[... more results ...]

======================================================================
TEST COMPLETE
======================================================================
```

---

## PHASE 10: VERIFY EVERYTHING WORKS

### Checklist:
- [ ] Server is running (terminal 1 shows "Application ready")
- [ ] http://localhost:8000/docs opens in browser
- [ ] quick_start.py ran successfully
- [ ] Test queries returned results with summaries
- [ ] No error messages

---

## TROUBLESHOOTING GUIDE

### Error: "Python version 3.12 required"
**Fix:** You're using wrong Python version
```bash
# Check version
python --version

# If not 3.12, recreate venv with:
py -3.12 -m venv venv  # Windows
python3.12 -m venv venv  # macOS/Linux
```

### Error: "No module named 'app'"
**Fix:** You're not in the project directory
```bash
# Make sure you see app/ folder
ls  # or "dir" on Windows

# If not, navigate to correct folder
cd path/to/research-assistant
```

### Error: "Could not find a version that satisfies the requirement torch"
**Fix:** Python version is incompatible
- You MUST use Python 3.12.x
- Delete venv and recreate with Python 3.12

### Error: "Port 8000 already in use"
**Fix:** Something is using port 8000
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Then access: http://localhost:8001/docs
```

### Error: "venv\Scripts\activate : cannot be loaded"
**Fix:** PowerShell execution policy (Windows only)
```bash
# Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or use Command Prompt instead of PowerShell
```

### Error: Installing packages fails
**Fix:** Upgrade pip and retry
```bash
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### Server starts but quick_start.py fails
**Fix:** Wait 30 seconds for model to load, then try again
```bash
# Wait for this message in server terminal:
# "✓ Embedding model loaded successfully"

# Then run in other terminal:
python quick_start.py
```

---

## VERIFICATION COMMANDS

Run these to verify everything is set up correctly:

```bash
# 1. Check Python version (must be 3.12.x)
python --version

# 2. Check if venv is activated (should show (venv))
# Windows:
echo %VIRTUAL_ENV%
# macOS/Linux:
echo $VIRTUAL_ENV

# 3. Check installed packages
pip list | grep -E "fastapi|uvicorn|torch|chromadb"

# 4. Test import (should have no output = success)
python -c "from app.main import app; print('✓ App imports successfully')"

# 5. Check if server is running
curl http://localhost:8000/health
```

---

## FOLDER STRUCTURE AFTER SETUP

```
research-assistant/
├── venv/                    # Virtual environment (CREATED)
│   ├── Scripts/             # Windows
│   ├── bin/                 # macOS/Linux
│   └── Lib/
├── data/                    # Auto-created when running
│   ├── documents/
│   └── chroma_db/
├── logs/                    # Auto-created when running
│   └── app.log
├── app/                     # Source code
│   ├── main.py
│   ├── config.py
│   ├── api/
│   ├── core/
│   ├── services/
│   └── models/
├── tests/
├── .env                     # Created from .env.example
├── requirements.txt
├── README.md
└── quick_start.py
```

---

## QUICK REFERENCE - COMMON COMMANDS

```bash
# Activate virtual environment
venv\Scripts\activate              # Windows
source venv/bin/activate           # macOS/Linux

# Start server
uvicorn app.main:app --reload

# Run tests
python quick_start.py

# Stop server
Ctrl+C

# Deactivate venv
deactivate

# View logs
# Windows:
type logs\app.log
# macOS/Linux:
tail -f logs/app.log
```

---

## SUCCESS INDICATORS

You know it's working when:
1. ✅ `python --version` shows 3.12.x inside venv
2. ✅ Server starts and shows "Application ready"
3. ✅ http://localhost:8000/docs loads in browser
4. ✅ `quick_start.py` runs without errors
5. ✅ Test queries return results with summaries

---

## NEXT STEPS AFTER SETUP

1. Read `README.md` for full documentation
2. Explore the API at http://localhost:8000/docs
3. Try ingesting your own text documents
4. Modify the code and experiment
5. Check `app/main.py` to understand the architecture

---

## GETTING HELP

If stuck:
1. Check the error message carefully
2. Look in the TROUBLESHOOTING GUIDE above
3. Check `logs/app.log` for detailed error info
4. Verify Python version is 3.12.x
5. Make sure venv is activated (you see (venv) in prompt)

---

## FILE VERSIONS

- Python: 3.12.8 (REQUIRED)
- FastAPI: 0.109.0
- Uvicorn: 0.27.0
- PyTorch: 2.1.2
- sentence-transformers: 2.3.1
- ChromaDB: 0.4.22

DO NOT modify requirements.txt versions - they are tested together.

---

END OF SETUP GUIDE
