
from flask_jwt_extended import create_access_token
import dotenv
import os



class Auth:
    def __init__(self):
        #Load env username and password
        dotenv.load_dotenv()
        self.username = os.getenv("USERNAME").lower()
        self.password = os.getenv("PASSWORD")
        self.access_token = None

    def check_credentials(self, username, password):
        print(username, password)
        print(self.username, self.password)

        return username == self.username and password == self.password
    
    def generate_token(self):
        self.access_token = create_access_token(identity=self.username)
        return self.access_token
    
