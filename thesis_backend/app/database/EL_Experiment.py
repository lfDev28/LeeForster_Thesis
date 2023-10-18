from app import db
from datetime import datetime


# Creating an embedded document to store the spectrometer values by their serial number
class SpectrometerValues(db.EmbeddedDocument):
    wavelengths = db.ListField(db.FloatField())
    spectrum = db.ListField(db.FloatField())
    dark_spectrum = db.ListField(db.FloatField())


class ElExperiment(db.Document):
    name = db.StringField()
    description = db.StringField()
    start_time = db.DateTimeField(required=True)
    end_time = db.DateTimeField()
    status = db.StringField()
    participants = db.ListField(db.StringField())
    metadata = db.DictField()
    voltage = db.ListField(db.FloatField())
    dark_spectrum = db.ListField(db.FloatField())
    values_by_spectrometer = db.DictField(
        db.EmbeddedDocumentField(SpectrometerValues))
    calibrated_values_by_spectrometer = db.DictField(
        db.EmbeddedDocumentField(SpectrometerValues))

    @staticmethod
    def create_experiment(name, description, metadata, participants, status):

        experiment = ElExperiment(
            name=name,
            description=description,
            start_time=datetime.utcnow(),
            end_time=None,
            participants=participants,
            metadata=metadata,
            status=status,
            values_by_spectrometer={},
            calibrated_values_by_spectrometer={}
        )

        experiment.save()
        return experiment

    @staticmethod
    def get_experiment_by_id(id):
        return ElExperiment.objects(id=id).first()

    @staticmethod
    def get_all_experiments():
        return ElExperiment.objects.all().order_by('-id')

    @staticmethod
    def delete_experiment_by_id(id):
        return ElExperiment.objects(id=id).delete()

    @staticmethod
    def mark_completed(id):
        experiment = ElExperiment.objects(id=id).first()
        experiment.update(status="Completed")
        experiment.update(end_time=datetime.now())
        return experiment

    @staticmethod
    def mark_failed(id):
        experiment = ElExperiment.objects(id=id).first()
        experiment.update(status="Failed")
        experiment.update(end_time=datetime.now())
        return experiment

    @staticmethod
    def update_experiment(id, name, description):
        experiment = ElExperiment.objects(id=id).first()
        experiment.update(
            name=name,
            description=description,
        )
        return experiment

    @staticmethod
    def add_metadata(id, metadata: dict):
        experiment = ElExperiment.objects(id=id).first()
        experiment.update(add_to_set__metadata=metadata)
        return experiment

    @staticmethod
    def add_wavelength_spectrum(id, wavelength: list[float], spectrum: list[float]):
        experiment = ElExperiment.objects(id=id).first()
        experiment.update(add_to_set__wavelengths=wavelength)
        experiment.update(add_to_set__spectrum=spectrum)
        return experiment

    @staticmethod
    def add_data_by_serial(experiment_id, serial_number, wavelengths: list[float], spectrum: list[float] ):
        experiment = ElExperiment.objects(id=experiment_id).first()

        update_dict = {
            f'set__values_by_spectrometer__{serial_number}__wavelengths': wavelengths,
            f'set__values_by_spectrometer__{serial_number}__spectrum': spectrum
        }

        experiment.update(**update_dict)

        return experiment
    
    @staticmethod
    def add_dark_spectrum_by_serial(experiment_id, serial_number, spectrum: list[float] ):
        experiment = ElExperiment.objects(id=experiment_id).first()

        update_dict = {
            f'set__values_by_spectrometer__{serial_number}__dark_spectrum': spectrum
        }

        experiment.update(**update_dict)

        return experiment

    @staticmethod
    def add_calibrated_data_by_serial(experiment_id, serial_number, wavelengths, spectrum):
        experiment = ElExperiment.objects(id=experiment_id).first()
        update_dict = {
            f'set__calibrated_values_by_spectrometer__{serial_number}__wavelengths': wavelengths,
            f'set__calibrated_values_by_spectrometer__{serial_number}__spectrum': spectrum
        }

        experiment.update(**update_dict)

    @staticmethod
    def add_metadata(experiment_id, key, value):
        experiment = ElExperiment.objects(id=experiment_id).first()
        update_dict = {
            f'set__metadata__{key}': value
        }

        experiment.update(**update_dict)

        return experiment
