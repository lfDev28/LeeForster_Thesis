@echo off

REM Run the splash screen
python splash_screen.py

REM Set current directory
SET current_dir=%cd%

cd %current_dir%

REM Run the Docker containers
docker-compose up -d

REM Open the web browser to your app
start http://localhost:3000

pause
