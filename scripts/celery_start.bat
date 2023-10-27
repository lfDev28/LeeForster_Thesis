@echo off
cd ../thesis_backend

.\venv\Scripts\activate

celery -A run.celery worker --pool=solo --loglevel=info
@REM exit