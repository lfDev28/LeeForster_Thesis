from app import create_app, ext_celery
from waitress import serve
import sys

app = create_app()

celery = ext_celery.celery


if __name__ == '__main__':
    # Check for linux or windows to run the app.
    if 'linux' in sys.platform:
        app.run(debug=True)
    else: 
        serve(app, host='127.0.0.1', port=8000)


