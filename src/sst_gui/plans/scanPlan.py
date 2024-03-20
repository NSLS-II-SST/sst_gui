from qtpy.QtWidgets import (
    QComboBox,
)
from qtpy.QtCore import Signal
from bluesky_queueserver_api import BPlan
from .base import PlanWidget


class TimescanWidget(PlanWidget):
    def __init__(self, model, parent=None):
        super().__init__(model, parent, steps=int, dwell=float, comment=str)
        self.display_name = "timescan"

    def check_plan_ready(self):
        params = self.get_params()

        if "steps" in params:
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def submit_plan(self):
        params = self.get_params()
        item = BPlan(
            "sst_count",
            params["steps"],
            dwell=params.get("dwell", None),
            comment=params.get("comment", None),
        )
        self.run_engine_client.queue_item_add(item=item)


class ScanPlanWidget(PlanWidget):
    signal_update_motors = Signal(object)

    def __init__(self, model, parent=None):
        # Make this into a more general base, and then add variants on top of it, i.e,
        # relscan, grid_scan, etc
        super().__init__(
            model, parent, start=float, end=float, steps=int, dwell=float, comment=str
        )
        print("Initializing Scan")
        self.display_name = "scan"
        self.motors = {}

        self.user_status.register_signal(
            "MOTOR_DESCRIPTIONS", self.signal_update_motors
        )
        self.signal_update_motors.connect(self.update_motors)

        # Create and add the scan related widgets here
        self.create_scan_modifier()
        print("Scan Initialized")

    def update_motors(self, plan_dict):
        inverted_dict = {}
        for key, value in plan_dict.items():
            inverted_dict[value] = key
        self.motors = inverted_dict
        self.noun_selection.clear()
        self.noun_selection.addItems(self.motors.keys())

    def create_scan_modifier(self):
        self.noun_selection = QComboBox(self)
        self.noun_selection.addItems(self.motors.keys())
        self.basePlanLayout.insertWidget(0, self.noun_selection)

    def check_plan_ready(self):
        params = self.get_params()
        check1 = "start" in params
        check2 = "end" in params
        check3 = "steps" in params
        if check1 and check2 and check3:
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        params = self.get_params()
        # start = float(self.modifier_input_from.text())
        # end = float(self.modifier_input_to.text())
        # steps = int(self.modifier_input_steps.text())
        item = BPlan(
            "sst_scan",
            motor,
            params["start"],
            params["end"],
            params["steps"],
            dwell=params.get("dwell", None),
            comment=params.get("comment", None),
        )
        self.run_engine_client.queue_item_add(item=item)
