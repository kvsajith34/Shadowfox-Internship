# Run Guide (Windows Friendly)

## Step 1: Open terminal in project folder
```bash
cd intelligent-autocorrect-keyboard
```

## Step 2: Create virtual environment
```bash
python -m venv venv
```

## Step 3: Activate virtual environment
```bash
venv\Scripts\activate
```

## Step 4: Install requirements
```bash
pip install -r requirements.txt
```

## Step 5: Run the Streamlit app
```bash
streamlit run app.py
```

## Step 6: Run tests
```bash
pytest tests/
```

## Common Error Fixes

### 1. streamlit is not recognized
- Cause: Streamlit is not installed in the active environment.
- Fix:
```bash
pip install streamlit
python -m streamlit run app.py
```

### 2. pyspellchecker import error
- Cause: Package missing or wrong package name installed.
- Fix:
```bash
pip install pyspellchecker
```

### 3. Virtual environment activation issue
- Cause: PowerShell execution policy blocks script activation.
- Fix:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then close and reopen terminal, and run:
```bash
venv\Scripts\activate
```