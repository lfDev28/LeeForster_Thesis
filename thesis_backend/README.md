# Flask Server ElEquant

## Key Information

### Spectrometer Modules

The spectrometers require the avaspecx64.dll file to be in the project, this file can be retrieved from avantis website if necessary, however it is in the project.
The Spectrometer python wrapper written by Avantis lives in the following directory: /backend/app/utils/avaspec.py
This wrapper gives functions to control the spectrometer with. Do not modify this file unless you know what you are doing and can document it accordingly as it is a wrapper around a C++ library.

### Virtual Environment

The project uses a virtual environment to manage the python packages used in the project. The virtual environment is located in the backend directory and is called venv. To activate the virtual environment, run the following command in the backend directory:

```
./venv/Scripts/activate
```

### Running the Server

To run the server, you must first install the python packages in the requirements.txt file. This can be done by running the following command in the backend directory:

```
pip install -r requirements.txt
```

Once the packages are installed, you can run the server by running the following command in the backend directory:

```
flask run
```

Running the Message Queue - Pre Docker Integration (Only executes on a single thread)
```
celery -A run.celery worker --pool=solo --loglevel=info
```

## Python Packages Information

### Flask

Is the web framework chosen for this project

### Flask-MongoEngine

Is an ORM that is used to interact with the MongoDB database, it is a wrapper around the pymongo package.
The package allows for type defining of schemas within a non-relational database, making it easier for
later developers to understand the structure of the database. Additionally, it provides an easier to use
API for querying and writing to the database.
