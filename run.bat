@echo off
REM Windows launcher
cd /d "%~dp0"

if not exist ".venv" (
  py -3 -m venv .venv
)
call .venv\Scripts\activate.bat
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt
streamlit run app.py
