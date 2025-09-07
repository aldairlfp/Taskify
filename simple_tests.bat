@echo off
REM Simple Test Runner for Windows
echo 🧪 Simple Taskify Tests
echo ========================

REM Check virtual environment
if "%VIRTUAL_ENV%"=="" (
    echo ⚠️  Please activate virtual environment first:
    echo .venv\Scripts\activate
    pause
    exit /b 1
)

echo ✅ Running simple tests...
echo.

REM Run simple tests
python run_simple_tests.py

echo.
echo 📝 To run individual test files:
echo   pytest tests/simple_test_api.py -v
echo   pytest tests/simple_test_core.py -v  
echo   pytest tests/simple_test_auth.py -v
echo   pytest tests/simple_test_tasks.py -v
echo.
pause
