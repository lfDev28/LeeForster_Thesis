from flask import Blueprint, abort, jsonify, request
import json
from ..database.Calibration import CalibrationDb
from ..utils.smu import Smu
from ..utils.spectrometer import Spectrometer
from ..utils.automation import Automation

bp = Blueprint('automation', __name__, url_prefix='/automation')

automation = Automation()

keyword_to_function_map = {
    "SET_VOLTAGE": automation.set_voltage,
    "SET_CURRENT": automation.set_current,
    "EL_MEASUREMENT": automation.el_experiment,
    "IV_SWEEP": automation.iv_experiment,
    "REPEAT_STEPS": automation.repeat_steps,
    "REPEAT_STEPS_DELAY": automation.repeat_steps_with_delay,
}


@bp.route("/automation", methods=["POST"])
def handle_tasks():
    try:
        data = request.get_json()
        smu_port = request.headers['smuPort']
        tasks = data["tasks"]

        for task in tasks:
            keyword = task['keyword']
            params = task['params']
            params['smuPort'] = smu_port

            # Check if the keyword exists in the map.
            if keyword in keyword_to_function_map:
                function_to_call = keyword_to_function_map[keyword]

                # For now, I'll assume that the keys in the `params` dictionary match the parameter names of the respective functions.
                # If this is not the case, you'll need to extract and pass the parameters appropriately.
                function_to_call.delay(**params)
            else:
                # Handle the error - a keyword was sent that the backend doesn't recognize.
                # You can either abort or handle this in another way that's appropriate for your application.
                abort(400, description=f"Invalid keyword: {keyword}")

        return jsonify({"status": "Tasks have been dispatched!"}), 200

    except Exception as e:
        print(e)
        return abort(400, "Failed to run automation: " + str(e))
