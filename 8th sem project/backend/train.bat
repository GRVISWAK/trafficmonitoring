@echo off
echo ============================================================
echo TRAINING ENHANCED ML MODELS
echo ============================================================
echo.
echo Models:
echo  - Isolation Forest (on normal windows only)
echo  - K-Means Clustering
echo  - Logistic Regression (misuse classification)
echo  - Failure Predictor (next-window prediction)
echo.
echo ============================================================

cd /d "c:\Users\HP\Desktop\8th sem project\backend"

echo.
echo Training enhanced models...
"C:/Users/HP/Desktop/8th sem project/.venv/Scripts/python.exe" train_models_enhanced.py

echo.
echo ============================================================
echo TRAINING COMPLETE
echo ============================================================
echo.
pause
