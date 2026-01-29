@echo off

echo =========================================
echo Setting up Backend
echo =========================================

cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo Training ML models...
python train_models.py

echo.
echo =========================================
echo Setting up Frontend
echo =========================================

cd ..\frontend

echo Installing npm dependencies...
call npm install

echo.
echo =========================================
echo Setup Complete!
echo =========================================
echo.
echo To start the backend:
echo   cd backend
echo   venv\Scripts\activate
echo   python app.py
echo.
echo To start the frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo =========================================

pause
