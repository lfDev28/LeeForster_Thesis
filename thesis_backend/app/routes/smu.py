from flask import Blueprint, abort, jsonify, request, send_file
import pyvisa
from pymeasure.instruments.keithley import Keithley2450
from app.utils.smu import Smu
from ..database.IV_Experiment import IvExperiment

bp = Blueprint('smu', __name__, url_prefix='/smu')



@bp.route('/connect', methods=["POST"])
def smu_connect():
    try:
        port = request.get_json()["port"]
        smu = Smu().connect(port)
        return jsonify({"message": "SMU connected successfully", "id": smu.id})
    except Exception as e:
        print(e)
        return abort(500, "Failed to connect to Smu: " + str(e)) 
    
@bp.route("/get-ports", methods=["GET"])
def get_ports():
    try:
        ports = pyvisa.ResourceManager().list_resources()
        return jsonify(ports)
    except Exception as e:
        print(e)
        return abort(500, "Failed to get ports: " + str(e))    

    
# DONE 
@bp.route("/iv/do_sweep_db", methods=["POST"])
def do_sweep_db():
    try:
        req = request.get_json()
        print(req)
        experiment_id = Smu().create_iv_experiment_db(request.headers["Smuport"], metadata=req["data"])

        print(f'Experiment ID: {experiment_id}')

        return jsonify({"id": str(experiment_id)})
        
    except Exception as e:
        print(e)
        return abort(400, "Failed to connect to perform IV sweep: " + str(e))

# DONE
@bp.route("/iv/read_csv", methods=["POST"])
def read_file():
    try:
        file = request.files['file']
        data = Smu().read_file(file)
        return jsonify(data)
    except Exception as e:
        print(e)
        return abort(400, "Failed to read file: " + str(e))

# TODO: Needs fixed
@bp.route("/iv/<id>/download", methods=["POST"])
def get_file():
    # Needs fixed
    try:
        req = request.get_json()
        experiment_id = req["experiment_id"]
        file_path = Smu().write_db_iv_experiment_to_csv(experiment_id)
        send_file(file_path, as_attachment=True)
        return jsonify({"message": "File sent successfully"})
    except Exception as e:
        print(e)
        return abort(400, "Failed to get file: " + str(e))


# DONE
@bp.route("/iv/write_file_to_db", methods=["POST"])
def write_file_to_db():
    try:
        file = request.files['file']
        data = Smu().write_file_to_db(file)
        return jsonify({"message": "File written to db successfully"})
    except Exception as e:
        print(e)
        return abort(400, "Failed to write file to db: " + str(e))


# DONE
@bp.route("/iv", methods=["GET"])
def get_all_iv_experiments():
    try:
        experiments = IvExperiment.get_all_experiments()
        return jsonify(experiments)
    except Exception as e:
        print(e)
        return abort(400, "Failed to get all iv experiments: " + str(e))

#  Get experiment by id


@bp.route("/iv/<id>", methods=["GET"])
def get_iv_experiment_by_id(id):
    try:
        print(id)
        experiment = IvExperiment.get_experiment_by_id(id)
        return jsonify(experiment)
    except Exception as e:
        print(e)
        return abort(400, "Failed to get iv experiment by id: " + str(e))


# Deleting a single experiment by id

@bp.route("/iv/<id>", methods=["DELETE"])
def delete_iv_experiment(id):
    try:
        IvExperiment.delete_experiment_by_id(id)
        return jsonify({"message": "IV experiment deleted successfully"})
    except Exception as e:
        print(e)
        return abort(400, "Failed to delete iv experiment: " + str(e))
    
@bp.route("/iv/<id>", methods=["PATCH"])
def update_iv_experiment(id):
    try:
        req = request.get_json()
        name = req["name"]
        description = req["description"]
        experiment = IvExperiment.update_experiment(id, name, description)
        return jsonify(experiment)
    except Exception as e:
        print(e)
        return abort(400, "Failed to update iv experiment: " + str(e))
