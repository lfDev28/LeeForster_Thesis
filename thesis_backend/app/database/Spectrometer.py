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
    def update_spectrometer(id, name, description, manufacturer, model, serial_number):
        spectrometer = SpectrometerDb.objects(id=id).first()
        spectrometer.update(
            name=name,
            description=description,
            manufacturer=manufacturer,
            model=model,
            serial_number=serial_number
            )
                            
        return spectrometer
    