import time
import pandas as pd
import numpy as np
from .avaspec import *
from ..database.EL_Experiment import ElExperiment
from ..database.Calibration import CalibrationDb
from ..database.Spectrometer import SpectrometerDb
from celery import shared_task
import os
from ..utils.smu import Smu



# Declaring constants for interpolating the specturm
INTERPOLATED_START_VIS = 350
INTERPOLATED_END_VIS = 1000
INTERPOLATED_START_NIR = 1001
INTERPOLATED_END_NIR = 1700
# Constants derived from Figure 3
H_PLANCK = 6.62607015E-34  # Planck's constant (h) in Joules seconds
C_LIGHT = 2.99792458E+17   # Speed of light (c) in nm/s
Q_ELECTRON = 1.60217662E-19  # Elementary charge (q) in Coulombs
J_PER_EV = Q_ELECTRON      # Energy of one electron volt in Joules (same as q)

# Ocean Insight calibration data as a dictionary
ocean_insight_data = {
    350.00: 3.35566E-01,
    360.00: 4.71780E-01,
    370.00: 6.30746E-01,
    380.00: 8.09485E-01,
    390.00: 1.01815E00,
    400.00: 1.26421E00,
    420.00: 1.87128E00,
    440.00: 2.66029E00,
    460.00: 3.65328E00,
    480.00: 4.85811E00,
    500.00: 6.27386E00,
    525.00: 8.31397E00,
    550.00: 1.06465E01,
    575.00: 1.32033E01,
    600.00: 1.59232E01,
    650.00: 2.16678E01,
    700.00: 2.74475E01,
    750.00: 3.27519E01,
    800.00: 3.71414E01,
    850.00: 4.07613E01,
    900.00: 4.37400E01,
    950.00: 4.64233E01,
    1000.00: 4.76631E01,
    1050.00: 4.84458E01,
    1100.00: 4.87223E01,
    1150.00: 4.86240E01,
    1200.00: 4.81349E01,
    1300.00: 4.63313E01,
    1540.00: 3.88200E01,
    1600.00: 3.69176E01,
    1700.00: 3.26404E01,
    2000.00: 2.36143E01,
    2100.00: 2.17216E01,
    2300.00: 1.77459E01,
    2400.00: 1.47701E01,
}

wavelengths = list(ocean_insight_data.keys())
values = list(ocean_insight_data.values())

# Interpolation
desired_wavelengths = np.arange(350, 1701, 1)  # Create an array from 350 to 1700 with a step of 1
interpolated_values = np.interp(desired_wavelengths, wavelengths, values)

# Convert the interpolated data back to a dictionary for further processing
interpolated_ocean_data = dict(zip(desired_wavelengths, interpolated_values))

def get_ocean_data(wavelength: float) -> float:
    """Returns the Ocean Insight spectrum value for a given wavelength."""
    # Find the closest available wavelength in the dictionary
    closest_wavelength = min(ocean_insight_data.keys(), key=lambda w: abs(w - wavelength))
    value = ocean_insight_data[closest_wavelength]
    if value == 0.0:
        raise ValueError(f"Ocean Insight data for wavelength: {closest_wavelength} is zero.")
    return value





class Spectrometer:
    def __init__(self):
        pass

    def disconnect(self, handle):
        try:
            return AVS_Deactivate(handle)

        except Exception as e:
            print(e)
            raise Exception(
                "Failed to disconnect from spectrometer: " + str(e))

    def get_devices(self):
        try:
            """
            This function gets a list of devices and stores their handle and serial number in a dict
            Serial number is necessary to be stored as that is the identifier we are using in the database
            to make the code more flexible for hotswapping spectrometers
            """
            AVS_Init(0)
            AVS_UpdateUSBDevices()
            device_list = AVS_GetList()
            devices = []
            for i in range(0, len(device_list)):
                device_info = {}
                handle = AVS_Activate(device_list[i])
                device_info["handle"] = handle
                device_info["serial_number"] = device_list[i].SerialNumber.decode(
                    "utf-8")
                devices.append(device_info)
                print("Device " + str(i) + " serial number: " + str(device_list[i].SerialNumber.decode(
                    "utf-8")) + " User Friendly Name: " + str(device_list[i].UserFriendlyName.decode("utf-8")))

            return devices
        except Exception as e:
            print(e)
            raise Exception("Failed to get number of devices: " + str(e))

    def connect(self, serial_number) -> bool:
        try:
            return AVS_GetHandleFromSerial(deviceSerial=serial_number)
        except Exception as e:
            print(e)
            raise Exception("Failed to connect to spectrometer: " + str(e))

    def read_file(self, file):
        try:
            metadata = []
            wavelengths = []
            energy = []
            spectralPower = []
            photonFlux = []

            df = pd.read_csv(
                file, skip_blank_lines=False, header=None, names=range(4))

            # Get the blank index for the voltage and current data
            blank_index = df.index[df.isnull().all(1)]

            # Iterate through the rows of the file until a blank line is found, storing the metadata in the dict
            # When a blank line is found skip one line and then store voltages and currents
            for index, row in df.iterrows():
                if pd.isnull(row[0]):
                    break
                metadata.append({row[0]: row[1]})

            for index, row in df.iloc[blank_index[0]+2:].iterrows():
                wavelengths.append(row[0])
                spectralPower.append(row[1])
                energy.append(row[2])
                photonFlux.append(row[3])

            return {"metadata": metadata, "wavelengths": wavelengths, "energy": energy, "spectralPower": spectralPower, "photonFlux": photonFlux}

        except Exception as e:
            print(e)
            raise Exception("Failed to read file: " + str(e))

    def configure_device(self, handle, integration_time, scans_to_average):
        try:
            # This method configures the device based on the use case we have predetermined.
            
            pixels = AVS_GetNumPixels(handle)
            cfg = MeasConfigType()
            cfg.m_IntegrationTime = int(integration_time)
            cfg.m_StopPixel = pixels - 1
            cfg.m_StartPixel = 0
            cfg.m_NrAverages = int(scans_to_average)
            cfg.m_CorDynDark_m_Enable = 0
            cfg.m_CorDynDark_m_ForgetPercentage = 100
            cfg.m_Smoothing_m_SmoothPix = 0
            cfg.m_Smoothing_m_SmoothModel = 0
            cfg.m_SaturationDetection = 0
            cfg.m_Trigger_m_Mode = 0
            cfg.m_Trigger_m_Source = 0
            cfg.m_Trigger_m_SourceType = 0
            cfg.m_Control_m_StrobeControl = 0
            cfg.m_Control_m_LaserDelay = 0
            cfg.m_Control_m_LaserWidth = 0
            cfg.m_Control_m_LaserWaveLength = 0.0
            cfg.m_Control_m_StoreToRam = 0

            return cfg, pixels

        except Exception as e:
            print(e)
            raise Exception("Failed to configure device: " + str(e))

    def get_spectrum_and_wavelength(self, handle: int, config: MeasConfigType, pixels: int):
        try:
            # Preparing wavelength array and storing the wavelengths
            wavelengths = []
            retLambda = AVS_GetLambda(handle)
            for pix in range(pixels):
                wavelengths.append(retLambda[pix])

            # Preparing the measurement and running it
            AVS_UseHighResAdc(handle, True)
            AVS_PrepareMeasure(handle, config)
            AVS_Measure(handle, 0, 1)

            # Loop until the data is ready
            dataready = False
            while not dataready:
                dataready = AVS_PollScan(handle)
            time.sleep(config.m_IntegrationTime / 1000)

            # Getting the spectrum data
            spectrum = []
            timestamp, scopedata = AVS_GetScopeData(handle)
            for i, pix in enumerate(wavelengths):
                spectrum.append(scopedata[i])

            # We then interpolate the wavelengths, the way we

            return wavelengths, spectrum

        except Exception as e:
            print(e)
            raise Exception("Failed to get spectrum and wavelength: " + str(e))

# Shared_Task decorator denotes a task that is going to be run in the background via the message queue
    @shared_task(bind=True)
    def do_el_experiment(self, experiment_id, current, integration_time, scans_to_average, port, compliance, cal_id):
        try:
            # Have to instantiate new spectrometer object because of the queue
            spectrometer = Spectrometer()
            devices = spectrometer.get_devices()
            smu = Smu()

            # First we capture a dark spectrum to later subtract from the raw spectrum

            # Loop through each spectrometer in the experiment
            for device in devices:
                print("Connecting to device: " + str(device["handle"]))
                cfg, pixels = spectrometer.configure_device(
                    device["handle"], integration_time, scans_to_average)

                raw_wavelengths, raw_spectrum = spectrometer.get_spectrum_and_wavelength(
                    device["handle"], cfg, pixels)

                # Interpolate the data first
                _, spectrum = spectrometer.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])

                # Store the dark spectrum in the database
                
                ElExperiment.add_dark_spectrum_by_serial(experiment_id, str(device["serial_number"]), spectrum)


            # Then we need to apply the current to the LED under test
            smu.set_current(port, current, compliance)
            time.sleep(2)


            voltage = smu.measure_voltage(port)

            # Adding the measured voltage to the metadata
            ElExperiment.add_metadata(
                experiment_id=experiment_id, key="Voltage (V)", value=voltage)

            experiment = ElExperiment.get_experiment_by_id(experiment_id)
            # Then take measurements for each spectrometer
            for device in devices:
                print("Connecting to device: " + str(device["handle"]))
                cfg, pixels = spectrometer.configure_device(
                    device["handle"], integration_time, scans_to_average)

                raw_wavelengths, raw_spectrum = spectrometer.get_spectrum_and_wavelength(
                    device["handle"], cfg, pixels)

                # Interpolate the data first
                wavelengths, spectrum = spectrometer.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])

                # We first subtract the raw data from the experiment
                
                dark_spectrum = experiment.values_by_spectrometer[device["serial_number"]].dark_spectrum

                corrected_spectrum = [raw - dark for raw, dark in zip(spectrum, dark_spectrum)]

                ElExperiment.add_data_by_serial(
                    experiment_id, str(device["serial_number"]), wavelengths, corrected_spectrum)
                spectrometer.disconnect(device["handle"])

            # Shutdown the SMU as we are finished with it here
            smu.shutdown()

            # We then apply the calibration, this method goes through the recent calibration file and applies it to the data.
            spectrometer.apply_calibration(experiment_id, cal_id)

            # Here we will do post processing to get total power and EL Quantum Yield, we will use the data from both spectrometers

            # # Fetch the experiment based on the provided ID
            # experiment = ElExperiment.get_experiment_by_id(experiment_id)

            # if not experiment:
            #     raise ValueError(f"No experiment found with ID: {experiment_id}")
            
            # # Stitch the wavelengths and spectra together

            # all_wavelengths = []
            # all_spectrum = []
            
            # for serial, spec_values in experiment.calibrated_values_by_spectrometer.items():
            #     all_wavelengths.extend(spec_values.wavelengths)
            #     all_spectrum.extend(spec_values.spectrum)

            # total_power = spectrometer.measure_total_power(all_spectrum, all_wavelengths)

            # ElExperiment.add_metadata(experiment_id, "Total Power (W)", total_power)

            # # Calculate the number of photons per second
            # photons_per_second = total_power / (H_PLANCK * C_LIGHT)

            # # Calculate the number of electrons per second
            # electrons_per_second = photons_per_second / Q_ELECTRON

            # quantum_yield = spectrometer.measure_quantum_yield(photons_per_second, electrons_per_second)

            # ElExperiment.add_metadata(experiment_id, "Quantum Yield (%)", quantum_yield)

            # Mark the experiment as completed in the database and then return to user
            finished_experiment = ElExperiment.mark_completed(experiment_id)

            return finished_experiment
        except Exception as e:
            print(e)
            ElExperiment.mark_failed(experiment_id)
            raise Exception("Failed to do el experiment: " + str(e))

    def create_experiment(self, metadata, port):
        try:
            experiment = ElExperiment.create_experiment(
                name="EL Experiment",
                description="EL Experiment",
                metadata=metadata,
                participants=["Participant 1", "Participant 2"],
                status="Running",
            )

            # Beginning the experiment in the queue
            self.do_el_experiment.delay(
                str(experiment.id), metadata["Current (mA)"], metadata["Integration Time (ms)"], metadata["Scans"], port, 10, metadata["calibration"])

            return str(experiment.id)

        except Exception as e:
            print(e)
            ElExperiment.mark_failed(experiment.id)
            raise Exception("Failed to create experiment: " + str(e))

    def list_spectrometers(self):
        # This method checks the ports for hte spectrometers and returns a list of them, additionally it gathers te serial number and user friendly name
        # And appends it to the spectrometer object
        try:
            ret = AVS_Init()
            ret = AVS_UpdateUSBDevices()
            list = AVS_GetList()
            Spectrometers = []
            for item in list:
                data = {}
                data["id"] = AVS_Activate(item)
                data["SerialNumber"] = item.SerialNumber.decode("utf-8")
                data["UserFriendlyName"] = item.UserFriendlyName.decode(
                    "utf-8")
                data["Status"] = item.Status.decode("utf-8")
                Spectrometers.append(data)

            return Spectrometers

        except Exception as e:
            print(e)
            raise Exception("Failed to list spectrometers: " + str(e))
        

    """  
    The below method will run in the background after the experiment has been completed 
    and will apply the calibration file to the spectrometer
    """

  
    def apply_calibration(self, experiment_id, cal_id) -> bool:
        try:
            print("applying cal")
            cal = CalibrationDb.get_calibration_by_id(cal_id)

            if not cal:
                raise ValueError("No calibration data found")

            # Fetch the experiment based on the provided ID
            experiment = ElExperiment.get_experiment_by_id(experiment_id)

            if not experiment:
                raise ValueError(f"No experiment found with ID: {experiment_id}")

            # Loop through each spectrometer in the experiment
            for serial, spec_values in experiment.values_by_spectrometer.items():
                print(serial)
                print(spec_values)
                
                if serial not in cal.calibration_by_serial:
                    raise ValueError(f"No calibration data for serial: {serial}")

                # Fetch the calibration data for this specific spectrometer
                cal_data = cal.calibration_by_serial[serial]

                # First we divide the spectrum by the calibration_spectrum
                spectral_radiance = [spectrum / calibration_spectrum for spectrum, calibration_spectrum in zip(spec_values.spectrum, cal_data.calibration_spectrum)]

                # Then we multiply by the raw spectrum
                spectral_radiance = [spectral_radiance * raw_spectrum for spectral_radiance, raw_spectrum in zip(spectral_radiance, spec_values.spectrum)]
                
            

                # Store the calibrated data (spectral radiance) back into the database
                ElExperiment.add_calibrated_data_by_serial(experiment_id, serial, spec_values.wavelengths, spectral_radiance)

            return True

        except Exception as e:
            print(f"Failed to apply calibration: {e}")
            return False


    def measure_total_power(self, spectrum, wavelengths):
        try:

            total_power = np.trapz(spectrum, wavelengths)

            return total_power
        
        except Exception as e:
            print(e)
            raise Exception("Failed to measure total power: " + str(e))
        
    def  measure_quantum_yield(self, photons_per_second, electrons_per_second):
        try:
            if electrons_per_second == 0:
                raise ValueError("Electrons per second cannot be zero")

            quantum_yield = (photons_per_second / electrons_per_second) * 100

            return quantum_yield
        
        except  Exception as e:
            print(e)
            raise Exception("Failed to measure quantum yield: " + str(e))
   

    # Placeholder method to add data based on the calibration files to the db. Can ignore.
    def add_cal_to_db(self, metadata={"test": "test"}):
        try:

            Desktop_Path = os.path.join(os.path.join(
                os.environ['USERPROFILE']), 'Desktop')

            cal_file_name = "test-cal.csv"

            cal_path = os.path.join(Desktop_Path, cal_file_name)

            cal_df = pd.read_csv(cal_path, skiprows=9, names=range(12))

            cal = CalibrationDb.new_calibration(metadata)

            for i in range(0, 12, 6):
                # Extracting serial number from the top cell in each group of 6 columns
                serial_number = cal_df.iloc[0, i]
                print(serial_number)

                wavelengths = cal_df.iloc[1:, i].tolist()
                dark_spectrum = cal_df.iloc[1:, i+1].tolist()
                dark_aux_spectrum = cal_df.iloc[1:, i+2].tolist()
                calibration_spectrum = cal_df.iloc[1:, i+3].tolist()
                aux_calibration_spectrum = cal_df.iloc[1:, i+4].tolist()
                aux_dut_spectrum = cal_df.iloc[1:, i+5].tolist()

                # remove NaN values if they exist
                wavelengths = [x for x in wavelengths if str(x) != 'nan']
                dark_spectrum = [x for x in dark_spectrum if str(x) != 'nan']
                dark_aux_spectrum = [
                    x for x in dark_aux_spectrum if str(x) != 'nan']
                calibration_spectrum = [
                    x for x in calibration_spectrum if str(x) != 'nan']
                aux_calibration_spectrum = [
                    x for x in aux_calibration_spectrum if str(x) != 'nan']
                aux_dut_spectrum = [
                    x for x in aux_dut_spectrum if str(x) != 'nan']
                

                CalibrationDb.add_calibration_by_serial(
                    cal_id=cal.id,
                    serial_number=str(serial_number),
                    wavelengths=wavelengths,
                    dark_spectrum=dark_spectrum,
                    dark_aux_spectrum=dark_aux_spectrum,
                    calibration_spectrum=calibration_spectrum,
                    aux_calibration_spectrum=aux_calibration_spectrum,
                    aux_dut_spectrum=aux_dut_spectrum
                )

            return True

        except Exception as e:
            print(e)
            raise Exception("Failed to add calibration to database: " + str(e))

    def get_calibration(self):
        try:
            return CalibrationDb.get_most_recent_calibration()
        except Exception as e:
            print(e)
            raise Exception("Failed to get calibration: " + str(e))

    def calibration_darks(self, cal_id):
        try:
            devices = self.get_devices()

            print("Calibrating darks")

            # 1st Loop for "Cal"
            for device in devices:
                print(f"Calibrating Cal for device: {device['handle']}")

                # Fetch spectrometer details using serial number
                spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(device["serial_number"])
                if not spectrometer_obj:
                    raise Exception(f"No spectrometer found with serial number {device['serial_number']}")

                integration_time = spectrometer_obj.cal_integration_time
                scans_to_average = spectrometer_obj.cal_scans_to_average

                if integration_time == 0.0 or scans_to_average == 0:
                    raise Exception(f"Calibration integration time or scans to average not set for spectrometer {device['serial_number']}")

                cfg, pixels = self.configure_device(device["handle"], integration_time, scans_to_average)
                raw_wavelengths, raw_spectrum = self.get_spectrum_and_wavelength(device["handle"], cfg, pixels)
                
                # Interpolating using the spectrometer's serial number
                wavelengths, spectrum = self.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])
                
                CalibrationDb.add_wavelengths(cal_id, str(device["serial_number"]), wavelengths)
                CalibrationDb.add_dark_spectrum(cal_id, str(device["serial_number"]), spectrum)

                # self.disconnect(device["handle"])

            time.sleep(3)

            # 2nd Loop for "Aux"
            for device in devices:
                print(f"Calibrating Aux for device: {device['handle']}")

                # Fetch spectrometer details using serial number
                spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(device["serial_number"])
                if not spectrometer_obj:
                    raise Exception(f"No spectrometer found with serial number {device['serial_number']}")

                print("Found spectrometer")
                integration_time = spectrometer_obj.aux_integration_time
                scans_to_average = spectrometer_obj.aux_scans_to_average

                print("Integration time: " + str(integration_time))
                if integration_time == 0.0 or scans_to_average == 0:
                    raise Exception(f"Aux integration time or scans to average not set for spectrometer {device['serial_number']}")

                print("Configuring device")
                cfg, pixels = self.configure_device(device["handle"], integration_time, scans_to_average)
                print("Getting spectrum and wavelength")
                raw_wavelengths, raw_spectrum = self.get_spectrum_and_wavelength(device["handle"], cfg, pixels)
                print("Interpolating spectrum")
                # Interpolating using the spectrometer's serial number
                wavelengths, spectrum = self.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])

                print("Adding wavelengths")
                CalibrationDb.add_dark_aux_spectrum(cal_id, str(device["serial_number"]), spectrum)

                self.disconnect(device["handle"])

            return

        except Exception as e:
            print(e)
            raise Exception(f"Failed to measure dark spectrum: {e}")


    def calibration_measure_cal(self, cal_id):
        try:
            devices = self.get_devices()
            
            for device in devices:
                print(f"Measuring Cal for device: {device['handle']}")

                # Fetch spectrometer details using serial number
                spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(device["serial_number"])
                if not spectrometer_obj:
                    raise Exception(f"No spectrometer found with serial number {device['serial_number']}")

                integration_time = spectrometer_obj.cal_integration_time
                scans_to_average = spectrometer_obj.cal_scans_to_average

                if integration_time == 0.0 or scans_to_average == 0:
                    raise Exception(f"Calibration integration time or scans to average not set for spectrometer {device['serial_number']}")

                cfg, pixels = self.configure_device(device["handle"], integration_time, scans_to_average)
                raw_wavelengths, raw_spectrum = self.get_spectrum_and_wavelength(device["handle"], cfg, pixels)

                # Interpolating using the spectrometer's serial number
                wavelengths, spectrum = self.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])
                    # Assuming you have a method to get Cal_dark data for this device
                cal_dark = CalibrationDb.get_cal_dark_data(cal_id, str(device["serial_number"]))

                # Step 2: Interpolate the ocean insight data
                interpolated_ocean_insight_data = np.interp(wavelengths, list(ocean_insight_data.keys()), list(ocean_insight_data.values()))

                # Step 3: Calculate the lamp factor (based on Figure 2)
                lamp_factor = [ocean_data / (cal - dark) for ocean_data, cal, dark in zip(interpolated_ocean_insight_data, spectrum, cal_dark)]

                # Store the Lamp factor in the DB
                CalibrationDb.add_lamp_factor(cal_id, str(device["serial_number"]), lamp_factor)

                # Conversion to photons/s/nm (based on Figure 3)
                photon_energy = [(H_PLANCK * C_LIGHT) / (wavelength * J_PER_EV) for wavelength in wavelengths]  # Photon energy (E) = h*c/lambda
                photons_spectrum = [spectral_power / energy for spectral_power, energy in zip(spectrum, photon_energy)] 

                # Store the converted data
                CalibrationDb.add_calibration_spectrum(cal_id, str(device["serial_number"]), photons_spectrum)


                self.disconnect(device["handle"])
                
            return

        except Exception as e:
            print(e)
            raise Exception(f"Failed to measure Cal: {e}")


    def calibration_measure_aux_cal(self, cal_id):
        try:
            devices = self.get_devices()

            for device in devices:
                print(f"Measuring Aux + Cal for device: {device['handle']}")

                # Fetch spectrometer details using serial number
                spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(device["serial_number"])
                if not spectrometer_obj:
                    raise Exception(f"No spectrometer found with serial number {device['serial_number']}")

                # Retrieve integration times
                cal_integration_time = spectrometer_obj.cal_integration_time
                cal_scans_to_average = spectrometer_obj.cal_scans_to_average

                aux_integration_time = spectrometer_obj.aux_integration_time  # Assuming you store this in your DB
                aux_scans_to_average = spectrometer_obj.aux_scans_to_average

                if cal_integration_time == 0.0 or aux_integration_time == 0.0:
                    raise Exception(f"Calibration or Aux integration time not set for spectrometer {device['serial_number']}")

                if cal_scans_to_average == 0 or aux_scans_to_average == 0:
                    raise Exception(f"Calibration or Aux scans to average not set for spectrometer {device['serial_number']}")
            
                # Configuring the device
                cfg, pixels = self.configure_device(device["handle"], aux_integration_time, aux_scans_to_average)  # Using Aux integration time
                raw_wavelengths, raw_spectrum = self.get_spectrum_and_wavelength(device["handle"], cfg, pixels)

                # Interpolating using the spectrometer's serial number
                wavelengths, spectrum = self.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])

                # Normalize spectrum based on integration times
                normalization_factor = cal_integration_time / aux_integration_time
                normalized_spectrum = [data * normalization_factor for data in spectrum]

                # Get the lamp factor from the database (assuming this function exists in CalibrationDb)
                lamp_factor = CalibrationDb.get_lamp_factor(cal_id, device["serial_number"])

                # Calculate spectral radiance (μW/nm)
                spectral_radiance = [norm_data * factor for norm_data, factor in zip(normalized_spectrum, lamp_factor)]

                # Store the spectral radiance (if needed, you can implement a method in CalibrationDb)
                CalibrationDb.add_aux_calibration_spectrum(cal_id, device["serial_number"], spectral_radiance)

                self.disconnect(device["handle"])

            return

        except Exception as e:
            print(e)
            raise Exception(f"Failed to measure Aux + Cal: {e}")



    def calibration_measure_aux_dut(self, cal_id, port):
        try:
            devices = self.get_devices()

            for device in devices:
                print(f"Measuring Aux + DUT for device: {device['handle']}")

                # Fetch spectrometer details using serial number
                spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(device["serial_number"])
                if not spectrometer_obj:
                    raise Exception(f"No spectrometer found with serial number {device['serial_number']}")

                # Retrieve integration times
                aux_integration_time = spectrometer_obj.aux_integration_time  # Assuming you store this in your DB

                if aux_integration_time == 0.0:
                    raise Exception(f"Aux integration time not set for spectrometer {device['serial_number']}")

                # Configuring the device
                cfg, pixels = self.configure_device(device["handle"], aux_integration_time, spectrometer_obj.cal_scans_to_average)
                raw_wavelengths, raw_spectrum = self.get_spectrum_and_wavelength(device["handle"], cfg, pixels)

                # Interpolating using the spectrometer's serial number
                wavelengths, spectrum_dut = self.interpolate_spectrum(raw_wavelengths, raw_spectrum, device["serial_number"])

                # Fetch the Aux + Cal spectrum data for this device from the DB
                spectrum_cal = CalibrationDb.get_aux_calibration_spectrum(cal_id, device["serial_number"])

                # Calculate the sphere calibration factor: Aux + Cal data divided by the Aux + DUT data
                sphere_calibration_factor = [cal_data / dut_data for cal_data, dut_data in zip(spectrum_cal, spectrum_dut)]

                # Store the sphere calibration factor
                CalibrationDb.add_sphere_calibration_factor(cal_id, device["serial_number"], sphere_calibration_factor)
                CalibrationDb.add_aux_dut_spectrum(cal_id, device["serial_number"], spectrum_dut)
                self.disconnect(device["handle"])

            return

        except Exception as e:
            print(e)
            raise Exception(f"Failed to measure Aux + DUT: {e}")


    def interpolate_spectrum(self, original_wavelengths, original_spectrum, serial_number, interval=1.0):
    
        try:
            # Fetch the spectrometer details based on the serial number
            spectrometer_obj = SpectrometerDb.get_spectrometer_by_serial(serial_number)
            if not spectrometer_obj:
                raise Exception(f"No spectrometer found with serial number {serial_number}")
            


            # Get desired interpolation range from the spectrometer object
            desired_start = spectrometer_obj.low_interpolation
            desired_end = spectrometer_obj.high_interpolation

            if desired_start == 0.0 or desired_end == 0.0 or desired_start == None or desired_end == None:
                raise Exception(f"Interpolation range not set for spectrometer {serial_number}")
            


            # Generate desired wavelength range
            desired_wavelengths = np.arange(desired_start, desired_end + interval, interval)

            # Perform linear interpolation
            interpolated_spectrum = np.interp(
                desired_wavelengths, original_wavelengths, original_spectrum)

            return desired_wavelengths, interpolated_spectrum

        except Exception as e:
            print(e)
            raise Exception("Failed to interpolate spectrum: " + str(e))


