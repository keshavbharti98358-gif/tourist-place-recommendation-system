@echo off
cd /d "%~dp0"
echo Installing required packages...
python -m pip install -r requirements.txt
echo.
echo Starting Tourist Place Recommendation System...
python app.py
pause
