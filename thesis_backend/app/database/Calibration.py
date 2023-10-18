from app import db
from datetime import datetime


class CalibrationBySerial(db.EmbeddedDocument):
    wavelengths = db.ListField(db.FloatField())
    dark_spectrum = db.ListField(db.FloatField())
    dark_aux_spectrum = db.ListField(db.FloatField())
    calibration_spectrum = db.ListField(db.FloatField())
    aux_calibration_spectrum = db.ListField(db.FloatField())
    aux_dut_spectrum = db.ListField(db.FloatField())
    lamp_factor = db.ListField(db.FloatField())
    sphere_calibration_factor = db.ListField(db.FloatField())


class CalibrationDb(db.Document):
    created_at = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField(default='In Progress')
    description = db.StringField()
    calibration_by_serial = db.DictField(
        db.EmbeddedDocumentField(CalibrationBySerial))
    metadata = db.DictField()


    @staticmethod
    def new_calibration(metadata={}):
        calibration = CalibrationDb(
            metadata=metadata,
            calibration_by_serial={},
            description="",
        )
        calibration.save()
        return calibration

    @staticmethod
    def get_all_calibrations():
        return CalibrationDb.objects.all().order_by('-id')

    @staticmethod
    def get_calibration_by_id(cal_id):
        return CalibrationDb.objects(id=cal_id).first()

    @staticmethod
    def update_calibration_by_id(cal_id, description):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)
        calibration.update(
            description=description
        )
        calibration.save()
        return calibration

    @staticmethod
    def get_most_recent_calibration():
        return CalibrationDb.objects().order_by('-created_at').first()

    @staticmethod
    def add_calibration_by_serial(cal_id, serial_number, wavelengths, dark_spectrum, dark_aux_spectrum, calibration_spectrum, aux_calibration_spectrum, aux_dut_spectrum):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)
        cal = {
            f'set__calibration_by_serial__{serial_number}__wavelengths': wavelengths,
            f'set__calibration_by_serial__{serial_number}__dark_spectrum': dark_spectrum,
            f'set__calibration_by_serial__{serial_number}__dark_aux_spectrum': dark_aux_spectrum,
            f'set__calibration_by_serial__{serial_number}__calibration_spectrum': calibration_spectrum,
            f'set__calibration_by_serial__{serial_number}__aux_calibration_spectrum': aux_calibration_spectrum,
            f'set__calibration_by_serial__{serial_number}__aux_dut_spectrum': aux_dut_spectrum
        }

        calibration.update(**cal)

        calibration.save()
        return calibration

    @staticmethod
    def add_wavelengths(cal_id, serial_number, wavelengths):
        print("adding wavelengths")
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        cal = {
            f'set__calibration_by_serial__{serial_number}__wavelengths': wavelengths,
        }

        calibration.update(**cal)
        calibration.save()
        return calibration

    @staticmethod
    def add_dark_spectrum(cal_id, serial_number, dark_spectrum):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        cal = {
            f'set__calibration_by_serial__{serial_number}__dark_spectrum': dark_spectrum,
        }

        calibration.update(**cal)
        calibration.save()
        return calibration

    @staticmethod
    def add_dark_aux_spectrum(cal_id, serial_number, dark_aux_spectrum):
        try:
            print("adding dark aux spectrum")
            calibration = CalibrationDb.get_calibration_by_id(cal_id)

            cal = {
                f'set__calibration_by_serial__{serial_number}__dark_aux_spectrum': dark_aux_spectrum,
            }

            calibration.update(**cal)
            calibration.save()
            return calibration
    
        except Exception as e:
            print(e)
            raise Exception(f"Failed to add dark aux spectrum: {str(e)}")

    @staticmethod
    def add_calibration_spectrum(cal_id, serial_number, calibration_spectrum):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        cal = {
            f'set__calibration_by_serial__{serial_number}__calibration_spectrum': calibration_spectrum,
        }

        calibration.update(**cal)
        calibration.save()
        return calibration

    @staticmethod
    def add_aux_calibration_spectrum(cal_id, serial_number, aux_calibration_spectrum):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        cal = {
            f'set__calibration_by_serial__{serial_number}__aux_calibration_spectrum': aux_calibration_spectrum,
        }

        calibration.update(**cal)
        calibration.save()
        return calibration

    @staticmethod
    def add_aux_dut_spectrum(cal_id, serial_number, aux_dut_spectrum):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        cal = {
            f'set__calibration_by_serial__{serial_number}__aux_dut_spectrum': aux_dut_spectrum,
        }

        calibration.update(**cal)
        calibration.save()
        return calibration

    @staticmethod
    def mark_completed(cal_id):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        calibration.update(
            status="Completed"
        )

        calibration.save()
        return calibration

    @staticmethod
    def delete_calibration(cal_id):
        return CalibrationDb.objects(id=cal_id).delete()
    
    @staticmethod
    def get_cal_dark_data(cal_id, serial_number):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)
        return calibration.calibration_by_serial[serial_number].dark_spectrum
    
    @staticmethod
    def add_lamp_factor(cal_id, serial_number, lamp_factor):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        update_dict = {
            f'set__calibration_by_serial__{serial_number}__lamp_factor': lamp_factor
        }

        calibration.update(**update_dict)

        calibration.save()
        return calibration
    
    @staticmethod
    def get_lamp_factor(cal_id, serial_number):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)
        return calibration.calibration_by_serial[serial_number].lamp_factor
    
    @staticmethod
    def add_sphere_calibration_factor(cal_id, serial_number, sphere_calibration_factor):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)

        update_dict = {
            f'set__calibration_by_serial__{serial_number}__sphere_calibration_factor': sphere_calibration_factor
        }

        calibration.update(**update_dict)

        calibration.save()
        return calibration

    @staticmethod 
    def get_aux_calibration_spectrum(cal_id, serial_number):
        calibration = CalibrationDb.get_calibration_by_id(cal_id)
        return calibration.calibration_by_serial[serial_number].aux_calibration_spectrum    