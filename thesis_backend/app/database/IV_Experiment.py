from app import db
from datetime import datetime

class IvExperiment(db.Document):
    name = db.StringField()
    description = db.StringField()
    start_time = db.DateTimeField(required=True)
    end_time = db.DateTimeField()
    status = db.StringField()
    participants = db.ListField(db.StringField())
    metadata = db.DictField()
    voltages = db.ListField(db.FloatField())
    currents = db.ListField(db.FloatField())

    @staticmethod
    def create_experiment(name, description, metadata, participants, voltages, currents, status):
        experiment = IvExperiment(
            name=name,
            description=description,
            start_time = datetime.utcnow(),
            end_time = None,
            participants=participants,
            metadata=metadata,
            voltages = voltages,
            currents = currents,
            status = status
        )
        
        experiment.save()
        return experiment

    @staticmethod
    def get_experiment_by_id(id):
        return IvExperiment.objects(id=id).first()

    @staticmethod
    def get_all_experiments():
        #  Getting all objects in reverse input order
         return IvExperiment.objects.all().order_by('-id')

    

    @staticmethod
    def delete_experiment_by_id(id: int):
        return IvExperiment.objects(id=id).delete()
    
    @staticmethod
    def mark_completed(id):
        experiment = IvExperiment.objects(id=id).first()
        experiment.update(status="Completed")
        experiment.update(end_time=datetime.utcnow())
        return experiment
    
    @staticmethod
    def mark_failed(id):
        experiment = IvExperiment.objects(id=id).first()
        experiment.update(status="Failed")
        experiment.update(end_time=datetime.utcnow())
        return experiment

    @staticmethod
    def update_experiment(id, name, description):
        experiment = IvExperiment.objects(id=id).first()
        experiment.update(
            name=name,
            description=description,
        )
        return experiment
    

    @staticmethod
    def add_metadata(id, metadata):
        experiment = IvExperiment.objects(id=id).first()
        experiment.update(add_to_set__metadata=metadata)
        return experiment

    @staticmethod
    def add_voltage_current(id, voltages, currents):
        experiment = IvExperiment.objects(id=id).first()
        experiment.update(__raw__={"$push": {"voltages": voltages}})
        experiment.update(__raw__={"$push": {"currents": currents}})
        return experiment
