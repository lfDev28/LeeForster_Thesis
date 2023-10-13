import pyvisa
from .avaspec import *
from ..database.Spectrometer import SpectrometerDb
from ..utils.spectrometer import Spectrometer
from serial.tools import list_ports

class Devices:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.devices = self.rm.list_resources()
        self.device = None

    def list_devices(self):
        return self.devices

    def list_spectrometers(self):
        try:
            ret = AVS_Init()
            ret = AVS_UpdateUSBDevices()
            list = AVS_GetList()
            SerialNumbers = []
            for item in list:
                data = {}
                data["id"] = AVS_Activate(item)
                data["SerialNumber"] = item.SerialNumber.decode("utf-8")
                data["UserFriendlyName"] = item.UserFriendlyName.decode(
                    "utf-8")
                data["Status"] = item.Status.decode("utf-8")
                SerialNumbers.append(data)

            return SerialNumbers
        except Exception as e:
            print(e)
            raise Exception("Failed to list spectrometers: " + str(e))

    def get_spectrometers_from_db(self):
        try:
            return SpectrometerDb.get_all_spectrometers()
        except Exception as e:
            print(e)
            raise Exception("Failed to list spectrometers: " + str(e))

    def get_spectrometer_by_id(self, id):
        try:
            return SpectrometerDb.get_spectrometer_by_id(id)
        except Exception as e:
            print(e)
            raise Exception("Failed to get spectrometer: " + str(e))

    def add_spectrometer_to_db(self, name, description, id, serial_number, manufacturer, model):
        try:
            SpectrometerDb.add_spectrometer(
                name=name, description=description, serial_number=serial_number, manufacturer=manufacturer, model=model)
        except Exception as e:
            print(e)
            raise Exception("Failed to add spectrometer: " + str(e))

    def connect_spectrometer_by_id(self, id):
        try:
            return Spectrometer.connect(id)
        except Exception as e:
            print(e)
            raise Exception("Failed to connect spectrometer: " + str(e))

    def get_smu_ports(self):
        try:
            return pyvisa.ResourceManager().list_resources()
        except Exception as e:
            print(e)
            raise Exception("Failed to get ports: " + str(e))

    def get_spectrometers(self):
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

            return spectrometers

        except Exception as e:
            print(e)
            raise Exception("Failed to get spectrometers: " + str(e))

    def get_serial_ports(self):
        try:
            ports = list_ports.comports()
            available_ports = []
            dict = {}
            for port in ports:
                dict["device"] = port.device
                dict["description"] = port.description
                dict["hwid"] = port.hwid
                available_ports.append(dict)
                dict = {}
            



            return available_ports
        except Exception as e:
            print(e)
            raise Exception("Failed to get ports: " + str(e))

    def get_dashboard_devices(self):
        try:
            spectrometers = self.get_spectrometers()
            serial_ports = self.get_serial_ports()
            smu_ports = self.get_smu_ports()

            return {"spectrometers": spectrometers, "serial_ports": serial_ports, "smu_ports": smu_ports}

        except Exception as e:
            print(e)
            raise Exception("Failed to get dashboard devices: " + str(e))
