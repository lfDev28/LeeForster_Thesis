from .smu import bp as smu_bp
from .spectrometer import bp as spectrometer_bp
from .connections import bp as connections_bp
from .calibration import  bp as calibration_bp
from .auth import bp as auth_bp

def register_routes(app):
    app.register_blueprint(smu_bp)
    app.register_blueprint(spectrometer_bp)
    app.register_blueprint(connections_bp)
    app.register_blueprint(calibration_bp)
    app.register_blueprint(auth_bp)
