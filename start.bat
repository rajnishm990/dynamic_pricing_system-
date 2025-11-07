@echo off
echo ========================================
echo Dynamic Menu Pricing System
echo Starting Application...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo Please install Docker Desktop for Windows
    pause
    exit /b 1
)

echo.
echo Starting PostgreSQL container...
docker-compose up -d

echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

echo.
echo Initializing database...
python -c "from app.db.database import init_db; init_db()"

echo.
echo ========================================
echo Starting FastAPI Server...
echo ========================================
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.

python run.py