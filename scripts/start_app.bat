@echo off
REM Start frontend
start cmd /c frontend_start.bat


REM Start Celery
start cmd /c celery_start.bat


REM Start backend
start cmd /c backend_start.bat


echo All services started!
pause
exit