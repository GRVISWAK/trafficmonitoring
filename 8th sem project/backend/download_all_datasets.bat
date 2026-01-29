@echo off
echo ============================================================
echo DOWNLOADING ALL SECURITY DATASETS
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call "..\.venv\Scripts\activate.bat"

echo.
echo Running multi-dataset downloader...
python datasets_manager.py

echo.
echo ============================================================
echo DOWNLOAD COMPLETE
echo ============================================================
echo.
echo Next: Run train.bat to train models on real datasets
echo Or: Run view_datasets.bat to view the downloaded data
echo.
pause
