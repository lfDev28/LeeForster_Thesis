@echo off

cd %~dp0\..\thesis_backend


if "%OS%"=="Windows_NT" (
    .\venv\Scripts\activate
    python run.py
) else (
    gunicorn app:app -b 0.0.0.0:8000
)
