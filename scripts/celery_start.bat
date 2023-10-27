@echo off

cd %~dp0\..\thesis_backend

if "%OS%"=="Windows_NT" (
    celery -A run.celery worker --pool=solo --loglevel=info
) else (
    celery -A run.celery worker --loglevel=info
)
