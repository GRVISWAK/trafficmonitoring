@echo off
echo ============================================================
echo EXPORT DATASETS FOR MENTOR DEMONSTRATION
echo ============================================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call "..\.venv\Scripts\activate.bat"

echo.
echo Exporting datasets to Excel, CSV, and comprehensive report...
python export_datasets.py

echo.
echo ============================================================
echo EXPORT COMPLETE
echo ============================================================
echo.
echo Files created in: backend\datasets\EXPORT_FOR_MENTORS\
echo.
echo You can now open these files:
echo   - TRAINING_DATASET.xlsx (Main dataset + statistics)
echo   - COMPLETE_DATASET_REPORT.txt (Comprehensive documentation)
echo   - DATASET_SUMMARY.csv (Quick reference)
echo.
pause
