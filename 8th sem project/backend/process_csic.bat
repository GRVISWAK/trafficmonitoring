@echo off
echo ============================================================
echo PROCESSING CSIC 2010 DATASET (CSV FORMAT)
echo ============================================================
echo.
echo Your file: backend\datasets\csic_database.csv
echo This script will process it into ML training features
echo.
echo ============================================================

cd /d "%~dp0"

echo.
echo Activating virtual environment...
call "..\.venv\Scripts\activate.bat"

echo.
echo Processing csic_database.csv...
python process_csic_csv.py

echo.
echo ============================================================
echo PROCESSING COMPLETE
echo ============================================================
echo.
echo Next: Run train.bat to train models on CSIC data
echo.
pause
