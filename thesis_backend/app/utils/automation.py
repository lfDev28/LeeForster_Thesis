from ..utils.smu import Smu
from ..utils.spectrometer import Spectrometer
from celery import shared_task
import time



class Automation():
    @shared_task(bind=True)
    def set_voltage(self, *args, **kwargs):
        try:
            port = kwargs["Smuport"]
            voltage = kwargs["Voltage (V)"]["value"]
            compliance = kwargs["Compliance (mA)"]["value"]


            smu = Smu().set_voltage(port, voltage, compliance)
            return smu
        except Exception as e:
            print(e)
            raise Exception(f"Failed to set voltage: {str(e)}")

    @shared_task(bind=True)
    def set_current(self, *args, **kwargs):
        try:
            port = kwargs["Smuport"]
            current = kwargs["Current (mA)"]["value"]
            compliance = kwargs["Compliance (V)"]["value"]

            smu = Smu().set_current(port, current, compliance)
            return smu
        except Exception as e:
            print(e)
            raise Exception(f"Failed to set current: {str(e)}")
    

    @shared_task(bind=True)
    def el_experiment(self, *args, **kwargs):
        try:
            port = kwargs["Smuport"]
            metadata = {
                "Current (mA)": kwargs["Current (mA)"]["value"],
                "Integration Time (ms)": kwargs["Integration Time (ms)"]["value"],
                "Scans": kwargs["Scans to Average"]["value"],
                "calibration": kwargs["Calibration"]["value"],
            }


            experiment_id = Spectrometer().create_experiment(metadata, port)
            return experiment_id
        except Exception as e:
            print(e)
            raise Exception(f"Failed to run EL experiment: {str(e)}")
        
    @shared_task(bind=True)
    def iv_experiment(self, *args , **kwargs):
        try:  

            # Get the port and metadata from the kwargs
            port = kwargs["Smuport"]
            
            metadata = {
                "Start (V)": kwargs["Start (V)"]["value"],
                "Stop (V)": kwargs["Stop (V)"]["value"],
                "Points": kwargs["Points"]["value"],
                "Compliance (mA)": kwargs["Compliance (mA)"]["value"],
                "Delay (s)": kwargs["Delay (s)"]["value"],
            }
        
            experiment_id = Smu().create_iv_experiment_db(port, metadata)
            return experiment_id
        except Exception as e:
            print(e)
            raise Exception(f"Failed to run IV experiment: {str(e)}")

    @shared_task(bind=True)
    def repeat_steps(self, *args, **kwargs):
        try:
            print("Repeating steps")
            """Repeats a subset of steps a given number of times."""
            start_step = kwargs["Step x"]["value"]
            end_step = kwargs["Step y"]["value"]
            repetitions = kwargs["Number of times"]["value"]
            tasks = kwargs["tasks"]

            # Extracting the sub-tasks to repeat
            # Assuming 1-indexed step numbers
            subset_tasks = tasks[start_step-1:end_step]
            print(subset_tasks)

            for _ in range(repetitions):
                for task in subset_tasks:
                    keyword = task["keyword"]
                    task_params = task.get("params", {})
                    keyword_to_function_map[keyword](**task_params, tasks=tasks)

        except Exception as e:
            print(f'Failed to repeat steps: {str(e)}')
            raise Exception(f"Failed to repeat steps: {str(e)}")

    @shared_task(bind=True)
    def repeat_steps_with_delay(self, *args, **kwargs):
        try:
            """Repeats a subset of steps with a delay between each step."""
            start_step = kwargs["Step x"]["value"]
            end_step = kwargs["Step y"]["value"]
            repetitions = kwargs["Number of times"]["value"]
            delay = kwargs["Delay (s)"]["value"]
            tasks = kwargs["tasks"]

            # Extracting the sub-tasks to repeat
            # Assuming 1-indexed step numbers
            subset_tasks = tasks[start_step-1:end_step]
            
            for _ in range(repetitions):
                for task in subset_tasks:
                    keyword = task["keyword"]
                    task_params = task.get("params", {})
                    keyword_to_function_map[keyword](**task_params, tasks=tasks)
                    time.sleep(delay)



        except Exception as e:
            print(f'Failed to repeat steps with delay: {str(e)}')
            raise Exception(f"Failed to repeat steps with delay: {str(e)}")
        
    @shared_task(bind=True)
    def delay(self, *args, **kwargs):
        try:
            """Delays for a given number of seconds."""
            delay = kwargs["Delay (s)"]["value"]
            time.sleep(delay)
        except Exception as e:
            print(f'Failed to delay: {str(e)}')
            raise Exception(f"Failed to delay: {str(e)}")



automation = Automation()

keyword_to_function_map = {
    "SET_VOLTAGE": automation.set_voltage,
    "SET_CURRENT": automation.set_current,
    "EL_MEASUREMENT": automation.el_experiment,
    "IV_SWEEP": automation.iv_experiment,
    "REPEAT_STEPS": automation.repeat_steps,
    "REPEAT_STEPS_DELAY": automation.repeat_steps_with_delay,
    "DELAY": automation.delay,
}