@echo off
cd %~dp0\..\thesis_backend

if "%OS%"=="Windows_NT" (
    .\venv\Scripts\python -m celery -A run.celery worker --pool=solo --loglevel=info
) else (
    celery -A run.celery worker --loglevel=info
)

pause

