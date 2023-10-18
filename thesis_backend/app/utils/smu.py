
from collections import OrderedDict
import csv
from datetime import datetime
from celery import shared_task
import numpy as N
import time
import os
from pymeasure.instruments.keithley import Keithley2450
import pandas as pd
from ..database.IV_Experiment import IvExperiment


class Smu:
    def __init__(self):
        pass
# DONE

    def connect(self, port):
        self.port = port
        try:
            keithley = Keithley2450(port)
            self.smu = keithley
        except:
            raise ConnectionError(
                "SMU is not connected, please ensure it is connected to the GPIB ports")
        return keithley
# DONE

    def shutdown(self):
        try:
            self.smu.shutdown()
        except Exception as e:
            raise Exception("Failed to shutdown SMU" + str(e))
# DONE

    def read_file(self, file):
        try:
            metadata = OrderedDict()
            voltages = []
            currents = []

            df = pd.read_csv(
                file, skip_blank_lines=False, header=None)

            # Get the blank index for the voltage and current data
            blank_index = df.index[df.isnull().all(1)]

            # Iterate through the rows of the file until a blank line is found, storing the metadata in the dict
            # When a blank line is found skip one line and then store voltages and currents
            for index, row in df.iterrows():
                if pd.isnull(row[0]):
                    break
                metadata[row[0].lstrip(":")] = row[1]

            for index, row in df.iloc[blank_index[0]+2:].iterrows():
                voltages.append(row[0])
                currents.append(row[1])

            return {"metadata": metadata, "voltages": voltages, "currents": currents}

        except Exception as e:
            print(e)
            raise Exception("Failed to read file: " + str(e))
# DONE

    def write_file_to_db(self, file):
        try:
            data = self.read_file(file)
            metadata = data["metadata"]
            voltages = data["voltages"]
            currents = data["currents"]

            experiment = IvExperiment.create_experiment(
                name="Test 1",
                description="First test of writing a file to the db",
                metadata=metadata,
                participants=["Participant 1", "Participant 2"],
                voltages=voltages,
                currents=currents,
                status="Completed"
            )

            return experiment

        except Exception as e:
            raise Exception("Failed to write file to db: " + str(e))

    # DONE

    def setup_voltage_source(self, port, compliance):
        try:
            keithley = self.connect(port)
            keithley.reset()  # Reseting the instrument
            time.sleep(1)
            # Setting the source to voltage
            keithley.use_rear_terminals()  # NEED THIS TO OUTPUT TO THE CORRECT TERMINAL
            keithley.apply_voltage()  # Setting the source to voltage
            keithley.compliance_current = compliance*1e-3  # Setting the compliance
            keithley.enable_source()  # Enabling the source
            keithley.measure_current()  # Setting up to measure current

            return keithley
        except ConnectionError as e:
            raise ConnectionError("Failed to connect to Smu: " + str(e))

    def IV_Sweep(self, port: list, metadata: dict):
        # Arrays for storing the voltages and currents
        try:
            voltages = []
            currents = []

            keithley = self.setup_voltage_source(
                port, metadata["Compliance (mA)"])

            # Performing the IV Sweep and storing the data in the arrays
            for V in N.linspace(start=metadata["Start (V)"], stop=metadata["Stop (V)"], num=metadata["Points"], endpoint=True):
                keithley.source_voltage = V
                keithley.enable_source()
                time.sleep(metadata["Delay (s)"])
                current = keithley.current
                voltages.append(V)
                currents.append(current)

            self.smu.shutdown()
            self.write_iv_to_csv(metadata, voltages, currents)
            # Returning the data to frontend
            return {"voltages": voltages, "currents": currents}

        except Exception as e:
            print(e)
            raise Exception("Failed to perform IV sweep: " + str(e))

    def IV_Sweep_db(self, port: list, metadata: dict):
        try:

            experiment = IvExperiment.create_experiment(
                name="IV Experiment",
                description="IV Experiment",
                metadata=metadata,
                participants=["Participant 1", "Participant 2"],
                voltages=[],
                currents=[],
                status="RUNNING"
            )

            keithley = self.setup_voltage_source(
                port, metadata["Compliance (mA)"])

            for V in N.linspace(start=metadata["Start (V)"], stop=metadata["Stop (V)"], num=metadata["Points"], endpoint=True):
                keithley.source_voltage = V
                time.sleep(metadata["Delay (s)"])
                current = keithley.current
                IvExperiment.add_voltage_current(experiment.id, V, current)

            finished_experiment = IvExperiment.mark_completed(experiment.id)

            self.smu.shutdown()
            return finished_experiment

        except Exception as e:
            IvExperiment.mark_failed(experiment.id)
            print(e)
            raise Exception("Failed to perform IV sweep: " + str(e))

    def write_iv_to_csv(self, metadata: dict, voltages: list, currents: list) -> str:
        try:
            home_dir = os.path.expanduser("~")
            directory = os.path.join(
                home_dir, "Desktop", "LeeForster", "IV_Data")
            if not os.path.exists(directory):
                os.makedirs(directory)

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            file_name = f'iv_data_{timestamp}.csv'
            file_path = os.path.join(directory, file_name)

            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)

                # Write the metadata rows
                writer.writerow(["Source", "Voltage"])

                for key, value in metadata.items():
                    writer.writerow([key, value])

                # Write the blank line
                writer.writerow([])
                # Write currents and voltage headers
                writer.writerow(["Voltage (V)", "Current (A)"])

                # Write the voltage and current data
                for voltage, current in zip(voltages, currents):
                    writer.writerow([voltage, current])

                print("IV data written to file")
                return file_path

        except Exception as e:
            print(e)
            raise Exception("Failed to create directory: " + str(e))

    def write_db_iv_experiment_to_csv(self, experiment_id: str) -> str:
        try:
            # Perform data fetching from the database with experiment_id

            # Placeholder data for now
            metadata = []
            voltages = []
            currents = []

            # Write the data to csv
            file_path = self.write_iv_to_csv(metadata, voltages, currents)
            return file_path

        except Exception as e:
            print(e)
            raise Exception("Failed to write experiment to csv: " + str(e))

    def create_iv_experiment_db(self, port: str, metadata: dict) -> str:
        try:
            experiment = IvExperiment.create_experiment(
                name="IV Experiment",
                description="",
                metadata=metadata,
                participants=["Participant 1"],
                voltages=[],
                currents=[],
                status="Running"
            )

            self.run_iv_experiment.delay(port, metadata, str(experiment.id))

            return experiment.id

        except Exception as e:
            print(e)
            raise Exception("Failed to create experiment: " + str(e))

    @shared_task(bind=True)
    def run_iv_experiment(self, port: str, metadata: dict, experiment_id: str) -> IvExperiment:
        try:
            print('Starting task - run_iv_experiment')
           
          
            keithley = Smu().setup_voltage_source(port, metadata["Compliance (mA)"])

                               
            for V in N.linspace(start=metadata["Start (V)"], stop=metadata["Stop (V)"], num=metadata["Points"], endpoint=True):
                keithley.source_voltage = V
                time.sleep(metadata["Delay (s)"])
                current = keithley.current
                IvExperiment.add_voltage_current(experiment_id, V, current)

                

            finished_experiment = IvExperiment.mark_completed(experiment_id)

            # self.smu.shutdown()
            return finished_experiment

        except Exception as e:
            IvExperiment.mark_failed(experiment_id)
            print(e)
            raise Exception("Failed to create experiment: " + str(e))

    def setup_current_source(self, port, current, compliance):
        try:
            keithley = self.connect(port)
            keithley.reset()  # Reseting the instrument
            time.sleep(1)
            # Setting the source to voltage
            keithley.source_current_range = 20e-3
            keithley.use_rear_terminals()  # NEED THIS TO OUTPUT TO THE CORRECT TERMINAL
            keithley.apply_current()  # Setting the source to current
            keithley.compliance_voltage = 20  # Setting the compliance
            keithley.enable_source()  # Enabling the source
            keithley.measure_voltage()  # Setting up to measure current
            

            return keithley
        except ConnectionError as e:
            raise ConnectionError("Failed to connect to Smu: " + str(e))

    def measure_voltage(self):
        try:
            return self.smu.voltage
        except Exception as e:
            raise Exception("Failed to measure voltage: " + str(e))

    def measure_current(self):
        try:
            return self.smu.current
        except Exception as e:
            raise Exception("Failed to measure current: " + str(e))
    # The following methods are used for the automation class

    def set_voltage(self, port, voltage, compliance):
        try:
            keithley = self.setup_voltage_source(port, compliance)
            keithley.source_voltage = voltage
            return "Voltage set to " + str(voltage) + "V"
        except Exception as e:
            raise Exception("Failed to set voltage: " + str(e))

    def set_current(self, port, current, compliance):
        try:
            keithley = self.setup_current_source(port, current, compliance)
            keithley.source_current = current * 1e-3 #mA conversion
            return "Current set to " + str(current) + "A"
        except Exception as e:
            raise Exception("Failed to set current: " + str(e))

    def measure_voltage(self, port):
        try:
            keithley = self.connect(port)
            return keithley.voltage
        except Exception as e:
            raise Exception("Failed to measure voltage: " + str(e))
