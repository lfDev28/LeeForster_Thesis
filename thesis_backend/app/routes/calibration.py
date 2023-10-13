from flask import Blueprint, abort, jsonify, request
from app.utils.calibration import Calibration
from ..database.Calibration import CalibrationDb
from ..utils.mcu import Arduino_Controller
from ..utils.spectrometer import Spectrometer

bp = Blueprint('calibration', __name__, url_prefix='/calibration')


@bp.route("/<id>", methods=["GET"])
def get_calibration(id):
    try:
        calibration = Calibration().get_calibration_by_id(id)

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(500, "Failed to get calibration: " + str(e))


@bp.route("/<id>", methods=["PATCH"])
def update_calibration(id):
    try:
        description = request.json["description"]
        calibration = CalibrationDb().update_calibration_by_id(id, description=description)

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(500, "Failed to update calibration: " + str(e))


@bp.route("/", methods=["GET"])
def get_all_calibrations():
    try:
        calibrations = CalibrationDb.get_all_calibrations()

        return jsonify(calibrations)

    except Exception as e:
        print(e)
        return abort(500, "Failed to get all calibrations: " + str(e))


@bp.route("/", methods=["POST"])
def create_new_calibration():
    try:
        req = request.get_json()

        calibration_id = CalibrationDb.new_calibration()

        return jsonify( calibration_id)

    except Exception as e:
        print(e)
        return abort(500, "Failed to create new calibration: " + str(e))
    
@bp.route("/<id>", methods=["DELETE"])
def delete_calibration(id):
    try:
        CalibrationDb.delete_calibration(id)

        return jsonify({"message": "Calibration deleted successfully"})

    except Exception as e:
        print(e)
        return abort(500, "Failed to delete calibration: " + str(e))
    
@bp.route("/calibration-lamp", methods=["POST"])
def control_calibration_lamp():
    try:
        state = request.get_json()["data"]["state"]
        print(state)
        port = request.headers["mcuPort"]
        mcu = Arduino_Controller(port)
        mcu.control_aux_lamp(state)
        mcu.close()
        
        
        return jsonify({"message": "Calibration lamp controlled successfully."})
    
    except Exception as e:
        print(e)
        return abort(500, f"Failed to control calibration lamp: {str(e)}")

@bp.route("/<id>/dark-spectrum", methods=["POST"])
def add_dark_spectrum_to_calibration(id):
    try:
        spectrometer = Spectrometer()
        spectrometer.calibration_darks(id)
        
        return jsonify({"message": "Dark spectrum added successfully."})
    
    except Exception as e:
        print(e)
        return abort(500, f"Failed to add dark spectrum: {str(e)}")


@bp.route("/<id>/calibration-spectrum", methods=["POST"])
def add_calibration_spectrum_to_calibration(id):
    try:
        spectrometer = Spectrometer()
        spectrometer.calibration_measure_cal(id)
        
        return jsonify({"message": "Calibration spectrum added successfully."})
    
    except Exception as e:
        print(e)
        return abort(500, f"Failed to add calibration spectrum: {str(e)}")


@bp.route("/<id>/aux-calibration-spectrum", methods=["POST"])
def add_aux_calibration_spectrum_to_calibration(id):
    try:
        spectrometer = Spectrometer()
        spectrometer.calibration_measure_aux_cal(id)
        
        return jsonify({"message": "Aux calibration spectrum added successfully."})
    
    except Exception as e:
        print(e)
        return abort(500, f"Failed to add aux calibration spectrum: {str(e)}")


@bp.route("/<id>/aux-dut-spectrum", methods=["POST"])
def add_aux_dut_spectrum_to_calibration(id):
    try:
        port = request.headers["Smuport"]    
        print(port)
        spectrometer = Spectrometer()
        spectrometer.calibration_measure_aux_dut(id, port)
        
        return jsonify({"message": "Aux DUT spectrum added successfully."})
    
    except Exception as e:
        print(e)
        return abort(500, f"Failed to add aux dut spectrum: {str(e)}")

