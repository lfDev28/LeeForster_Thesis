import os
import subprocess
import webbrowser
import time

# Currently in the desktop path so well leave it there, first we change directory to desktop path
desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
project_path = os.path.join(desktop_path, 'LeeForster_ElEquantPy')



os.chdir(project_path)

# Launch splash screen
subprocess.run(['python', 'splash_screen.py'])


# Run docker-compose
subprocess.run(['docker-compose', 'up', '-d'])

# Give it a little time before launching the browser
time.sleep(5)

# Open the web browser
webbrowser.open('http://localhost:3000')
