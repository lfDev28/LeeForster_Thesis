from ..utils.smu import Smu
from ..utils.spectrometer import Spectrometer
from celery import SharedTask
from ..routes.automation import keyword_to_function_map
import time


class Automation():
    @SharedTask(bind=True)
    def set_voltage(self, port, voltage, compliance):
        smu = Smu().set_voltage(port, voltage, compliance)
        return smu

    @SharedTask(bind=True)
    def set_current(self, port, current, compliance):
        smu = Smu().set_current(port, current, compliance)
        return smu

    @SharedTask(bind=True)
    def el_experiment(self, metadata, smuPort):
        experiment_id = Spectrometer().create_experiment(metadata, smuPort)
        return experiment_id

    @SharedTask(bind=True)
    def iv_experiment(self, metadata, port):
        experiment_id = Smu().create_iv_experiment_db(metadata, port)

        return experiment_id

    @SharedTask(bind=True)
    def repeat_steps(self, params, tasks):
        """Repeats a subset of steps a given number of times."""
        start_step = params["Step x"]
        end_step = params["Step y"]
        repetitions = params["Number of times"]

        # Extracting the sub-tasks to repeat
        # Assuming 1-indexed step numbers
        subset_tasks = tasks[start_step-1:end_step]

        for _ in range(repetitions):
            for task in subset_tasks:
                keyword = task["keyword"]
                task_params = task.get("params", {})
                keyword_to_function_map[keyword](task_params, tasks)


def repeat_steps_with_delay(self, params, tasks):
    """Repeats a subset of steps with a delay between each step."""
    delay = params["Delay (s)"]
    self.repeat_steps(params, tasks)
    time.sleep(delay)
