#!/bin/bash

echo "========================================="
echo "Setting up Backend"
echo "========================================="

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Training ML models..."
python train_models.py

echo ""
echo "========================================="
echo "Setting up Frontend"
echo "========================================="

cd ../frontend

echo "Installing npm dependencies..."
npm install

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "  python app.py"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "========================================="
