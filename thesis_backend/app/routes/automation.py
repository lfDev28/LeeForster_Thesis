from flask import Blueprint, abort, jsonify, request
import json
from ..database.Calibration import CalibrationDb
from ..utils.smu import Smu
from ..utils.spectrometer import Spectrometer
from ..utils.automation import keyword_to_function_map

bp = Blueprint('automation', __name__, url_prefix='/automation')



@bp.route("/", methods=["POST"])
def handle_tasks():
    try:
        print("Got to handle tasks")
        tasks = request.get_json()
        smu_port = request.headers["Smuport"]
        notification_email = tasks["Notification Email"]

  

        for task in tasks:
            keyword = task['keyword']
            params = task['params']
            params['Smuport'] = smu_port
            params['Notification Email'] = notification_email
            # If its the final step, we add a "final" kwarg to the function call.
            if task == tasks[-1]:
                params['final'] = True


            # Check if the keyword exists in the map.
            if keyword in keyword_to_function_map:
                function_to_call = keyword_to_function_map[keyword]

                # If the function is one of the repition functions, we will have to pass it the tasks as well.
                if keyword in ["REPEAT_STEPS", "REPEAT_STEPS_DELAY"]:
                    function_to_call.delay(**params, tasks=tasks)
                else:
                    function_to_call.delay(**params)
            else:
         
                abort(400, description=f"Invalid keyword: {keyword}")

        return jsonify({"status": "Tasks have been dispatched!"}), 200

    except Exception as e:
        print(e)
        return abort(400, "Failed to run automation: " + str(e))
