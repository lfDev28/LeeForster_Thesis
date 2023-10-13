from flask import Blueprint, request, jsonify, abort
from ..utils.auth import Auth


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/login', methods=["POST"])
def login():
    try:
    
        if not request.is_json:
            return abort(400, "Missing JSON in request")
        
        username = request.json.get('username', None)
        password = request.json.get('password', None)

        if not username:
            return abort(400, "Missing username parameter")
        
        if not password:
            return abort(400, "Missing password parameter")
        

        auth = Auth()

        if not auth.check_credentials(username, password):
            return abort(401, "Incorrect username or password")
        
        access_token = auth.generate_token()
        return jsonify(access_token=access_token), 200

    except Exception as e:
        print(e)
        return abort(500, "Failed to login: " + str(e))


@bp.route('/logout', methods=["POST"])
def logout():

    return jsonify({"message": "Successfully logged out"}), 200

    
    


