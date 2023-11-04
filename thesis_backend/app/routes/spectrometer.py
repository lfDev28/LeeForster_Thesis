from flask import Blueprint, abort, jsonify, request, send_file
from app.utils.spectrometer import Spectrometer
from ..database.EL_Experiment import ElExperiment
from ..database.Spectrometer import SpectrometerDb
import json
from ..database.Calibration import CalibrationDb

bp = Blueprint('spectrometer', __name__, url_prefix='/spectrometer')


@bp.route('/connect', methods=["POST"])
def spectrometer_connect():
    try:
        device_id = request.get_json()["id"]
        Spectrometer().connect(device_id)

        return jsonify({"message": "Connected to Spectrometer"})

    except Exception as e:
        print(e)
        return abort(500, "Failed to connect to Spectrometer: " + str(e))


@bp.route("/read_el_file", methods=['POST'])
def read_example():
    try:
        file = request.files["file"]
        data = Spectrometer().read_file(file)
        return jsonify(data)
    except Exception as e:
        print(e)
        return abort(400, "Failed to connect to Smu: " + str(e))


@bp.route("/el/do_el_experiment", methods=['POST'])
def do_el_measurement():
    try:
        # Calls the create_experiment method which calls the do_el_experiment method and puts it into the message queue
        metadata = request.get_json()["data"]

        experiment_id = Spectrometer().create_experiment(
            metadata, request.headers["Smuport"])
        return jsonify({"id": experiment_id})

    except Exception as e:
        print(e)
        return abort(400, "Failed to nnect to Smu: " + str(e))


@bp.route("/el/<id>", methods=['GET'])
def get_el_by_id(id):
    try:
        # Get the experiment then concatenate the data from each spectrometer for the frontend to display
        experiment = ElExperiment.get_experiment_by_id(id)
        experiment = experiment.to_mongo().to_dict()
        experiment["wavelengths"] = []
        experiment["spectrum"] = []

        """
        Stitching the data for each spectrometer together, this needs to be abstracted to a method that stitches
        the spectrometers data as well as corrects it using the calibration files
        """

        for key, value in experiment["calibrated_values_by_spectrometer"].items():
            experiment["wavelengths"] += value["wavelengths"]
            experiment["spectrum"] += value["spectrum"]

        # Now the objectId is not serializable so we have to convert it to a string
        experiment["_id"] = str(experiment["_id"])


        # Removing values_by_spectrometer because it is not needed for the frontend and is a lot of data
        del experiment["calibrated_values_by_spectrometer"]
        del experiment["values_by_spectrometer"]

        return jsonify(experiment)
    except Exception as e:
        print(e)
        return abort(400, "Failed to connect to get experiment: " + str(e))


@bp.route("/el/<id>", methods=['DELETE'])
def delete_el_by_id(id):
    try:
        experiment = ElExperiment.delete_experiment_by_id(id)
        return jsonify(experiment)
    except Exception as e:
        print(e)
        return abort(400, "Failed to connect to delete experiment: " + str(e))


@bp.route("/el", methods=['GET'])
def get_all_el():
    try:
        experiments = ElExperiment.get_all_experiments()
        return jsonify(experiments)
    except Exception as e:
        print(e)
        return abort(400, "Failed to connect to get experiments: " + str(e))


@bp.route("/el/<id>", methods=["PATCH"])
def update_el_experiment(id):
    try:
        print("attempting")
        req = request.get_json()
        name = req["name"]
        description = req["description"]
        experiment = ElExperiment.update_experiment(id, name, description)
        return jsonify(experiment)
    except Exception as e:
        print(e)
        return abort(400, "Failed to update experiment: " + str(e))


@bp.route("/", methods=["POST"])
def add_spectrometer_to_db():
    try:
        req = request.get_json()

        spectrometer = Spectrometer.add_spectrometer_to_db(
            name=req["name"], description=req["description"], serial_number=req["serial_number"], manufacturer=req["manufacturer"], model=req["model"])
        return jsonify(spectrometer)

    except Exception as e:
        print(e)
        return abort(500, "Failed to add spectrometer to database: " + str(e))


@bp.route("/", methods=["GET"])
def get_all_spectrometers():
    try:
        spectrometers_from_db = SpectrometerDb.get_all_spectrometers()

        list = Spectrometer().list_spectrometers()
        if list is None:
            raise Exception("No spectrometers found")

        for newSpec in list:
            # Add check for if there are no spectrometers in the db
            if len(spectrometers_from_db) == 0:
                SpectrometerDb.add_spectrometer(
                    name="New Spectrometer", description="", serial_number=newSpec["SerialNumber"], manufacturer="", model="")
            else:
                for dbSpec in spectrometers_from_db:
                    if newSpec["SerialNumber"] == dbSpec["serial_number"]:
                        break
                    # If we have reached the end of the list and not found it, then it is not in the db so we add it
                    if dbSpec == spectrometers_from_db[len(spectrometers_from_db) - 1]:
                        SpectrometerDb.add_spectrometer(
                            name="New Spectrometer", description="", serial_number=newSpec["SerialNumber"], manufacturer="", model="")

        spectrometers = SpectrometerDb.get_all_spectrometers()

        return jsonify(spectrometers)
    except Exception as e:
        print(e)
        return abort(400, "Failed to get all spectrometers: " + str(e))


@bp.route("/<id>", methods=["GET"])
def get_spectrometer_by_id(id):
    try:
        spectrometer = SpectrometerDb.get_spectrometer_by_id(id)
        return jsonify(spectrometer)
    except Exception as e:
        print(e)
        return abort(400, "Failed to get spectrometer by id: " + str(e))


@bp.route("/<id>", methods=["DELETE"])
def delete_spectrometer_by_id(id):
    try:
        spectrometer = SpectrometerDb.delete_spectrometer_by_id(id)
        return jsonify(spectrometer)
    except Exception as e:
        print(e)
        return abort(400, "Failed to delete spectrometer by id: " + str(e))


@bp.route("/<id>", methods=["PATCH"])
def update_spectrometer_by_id(id):
    try:
        req = request.get_json()

        spectrometer = SpectrometerDb.update_spectrometer(
            id, name=req["name"], description=req["description"], serial_number=req["serial_number"], manufacturer=req["manufacturer"], model=req["model"], low_interpolation=req["low_interpolation"], high_interpolation=req["high_interpolation"], cal_integration_time=req["cal_integration_time"], cal_scans_to_average=req["cal_scans_to_average"], aux_integration_time=req["aux_integration_time"], aux_scans_to_average=req["aux_scans_to_average"])
        return jsonify(spectrometer)
    except Exception as e:
        print(e)
        return abort(400, "Failed to update spectrometer by id: " + str(e))


@bp.route("/<id>/connect", methods=["POST"])
def connect_spectrometer_by_id(id):
    try:
        # get serial number from db from id
        spectrometer = SpectrometerDb.get_spectrometer_by_id(id)
        serial_number = spectrometer["serial_number"]
        handle = Spectrometer().connect(serial_number)

        # Successfully connected so mark in DB for recent connection
        if handle is not None:
            SpectrometerDb.mark_connected(id)

        return jsonify({"message": "Connected to Spectrometer"})

    except Exception as e:
        print(e)
        return abort(400, "Failed to connect spectrometer by id: " + str(e))


@bp.route("/calibration", methods=["GET"])
def get_most_recent_calibration():
    try:
        calibration = Spectrometer().get_calibration()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration", methods=["POST"])
def new_calibration():
    try:
        calibration = CalibrationDb.new_calibration()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration/dark", methods=["POST"])
def calibrate_darks():
    try:
        calibration = Spectrometer().calibration_darks()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration/cal", methods=["POST"])
def calibration_cal():
    try:
        calibration = Spectrometer().calibration_measure_cal()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration/cal-aux", methods=["POST"])
def calibration_aux_cal():
    try:
        calibration = Spectrometer().calibration_measure_aux_cal()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration/aux-dut", methods=["POST"])
def calibration_aux_dut():
    try:
        calibration = Spectrometer().calibration_measure_aux_dut()

        return jsonify(calibration)

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))


@bp.route("/calibration/lamp", methods=["POST"])
def control_aux_lamp():
    try:
        # Get default request headers for the arduino port
        port = request.headers["Arduinoport"]
        # Get the request body
        req = request.get_json()
        # Get the action from the request body
        action = req["action"]

        Spectrometer().control_aux_lamp(action)

        return jsonify({"message": "Lamp state changed successfully"})

    except Exception as e:
        print(e)
        return abort(400, "Failed to get calibration: " + str(e))

@bp.route("/el/<id>/download", methods=["GET"])
def send_el_as_csv(id):
    try:
        spectrometer = Spectrometer()

        file_path = spectrometer.write_db_el_to_csv(id)

        return send_file(file_path, as_attachment=True, mimetype="text/csv", download_name=file_path.split("/")[-1])    

    except Exception as e:
        print(e)
        return abort(400, "Failed to create csv from experiment: " + str(e))
    
@bp.route("/el/upload", methods=["POST"])
def upload_csv_to_db():
    try:
        spectrometer = Spectrometer()
        file = request.files["file"]
        spectrometer.write_csv_el_to_db(file)
        return jsonify({"message": "CSV uploaded successfully"})
    except Exception as e:
        return abort(400, "Failed to upload csv to db: " + str(e))
    
