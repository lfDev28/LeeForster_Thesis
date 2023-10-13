from ..database.Spectrometer import SpectrometerDb
from ..database.Calibration import CalibrationDb
from ..utils.spectrometer import Spectrometer


class Calibration:
    def __init__(self):
        pass

    def get_calibration_by_id(self, id):
        try:
            return CalibrationDb.get_calibration_by_id(id)
        except Exception as e:
            print(e)
            raise Exception("Failed to get calibration: " + str(e))
