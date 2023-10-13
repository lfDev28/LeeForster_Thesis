from flask import Blueprint, abort, jsonify, request
from app.utils.connections import Devices
from app.utils.spectrometer import Spectrometer

bp = Blueprint('connections', __name__, url_prefix='/devices')


@bp.route("/scan", methods=["GET"])
def scan_devices():
    try:
        devices = Devices()
        device_list = devices.list_devices()
        spectrometers = devices.list_spectrometers()
        return jsonify({"devices": device_list, "spectrometers": spectrometers})
    except Exception as e:
        print(e)
        return abort(500, "Failed to scan for devices: " + str(e))


@bp.route("/spectrometers", methods=["GET"])
def get_spectrometers():
    try:
        devices = Devices()
        spectrometers = devices.get_spectrometers_from_db()
        if spectrometers.length == 0:
            spectrometers = devices.list_spectrometers()

        return jsonify({"spectrometers": spectrometers})
    except Exception as e:
        print(e)
        return abort(500, "Failed to get spectrometers: " + str(e))


@bp.route("/", methods=["GET"])
def get_dashboard_data():
    try:
        data = Devices().get_dashboard_devices()

        return jsonify(data)

    except Exception as e:
        print(e)
        return abort(500, "Failed to get dashboard data: " + str(e))
