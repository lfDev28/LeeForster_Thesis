from app import db
from datetime import datetime

class SpectrometerDb(db.Document):
    name = db.StringField()
    description = db.StringField()
    serial_number = db.StringField()
    last_connected = db.DateTimeField()
    manufacturer = db.StringField()
    model = db.StringField()
    handle = db.IntField()
    low_interpolation = db.FloatField(default=0.0)
    high_interpolation = db.FloatField(default=0.0)
    aux_integration_time = db.FloatField(default=0.0)
    aux_scans_to_average = db.IntField(default=0)
    cal_integration_time = db.FloatField(default=0.0)
    cal_scans_to_average = db.IntField(default=0)
    
    
    @staticmethod
    def add_spectrometer(name, description, serial_number, manufacturer, model):    
        spectrometer = SpectrometerDb(
            name=name,
            description=description,
            serial_number = serial_number,
            last_connected = datetime.now(),
            manufacturer=manufacturer,
            model=model
        )
        spectrometer.save()
        return spectrometer
    
    @staticmethod
    def get_spectrometer_by_id(id):
        return SpectrometerDb.objects(id=id).first()
    
    @staticmethod
    def get_spectrometer_by_serial(serial_number):
        return SpectrometerDb.objects(serial_number=serial_number).first()
    
    @staticmethod
    def get_all_spectrometers():
            return SpectrometerDb.objects.all().order_by('-id')
    
    @staticmethod
    def delete_spectrometer_by_id(id: int):
        return SpectrometerDb.objects(id=id).delete()
    
    @staticmethod
    def mark_connected(id):
        spectrometer = SpectrometerDb.objects(id=id).first()
        spectrometer.update(last_connected=datetime.utcnow())
        return spectrometer
    
    @staticmethod
    def update_spectrometer(id, name, description, manufacturer, model, serial_number, low_interpolation, high_interpolation, cal_integration_time, cal_scans_to_average):
        spectrometer = SpectrometerDb.objects(id=id).first()
        spectrometer.update(
            name=name,
            description=description,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number,
            low_interpolation=low_interpolation,
            high_interpolation=high_interpolation,
            cal_integration_time=cal_integration_time,
            cal_scans_to_average=cal_scans_to_average
            )
                            
        return spectrometer
    

    