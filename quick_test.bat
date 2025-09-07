@echo off
REM Quick test runner for Windows
echo 🧪 Taskify Quick Test Runner
echo ============================

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Warning: Virtual environment not detected
    echo Please activate your virtual environment first:
    echo .venv\Scripts\activate
    pause
    exit /b 1
)

echo ✅ Virtual environment detected: %VIRTUAL_ENV%

REM Install dependencies
echo.
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Run basic tests
echo.
echo 🧪 Running basic tests...
pytest tests/test_models.py tests/test_auth.py -v
if %errorlevel% neq 0 (
    echo ❌ Basic tests failed
    pause
    exit /b 1
)

echo.
echo 🎉 Quick tests passed!
echo.
echo 🚀 To run all tests with coverage:
echo    pytest tests/ --cov=app --cov-report=html
echo.
echo 📊 To run performance tests:
echo    pytest tests/test_performance.py -v
echo.
pause
