from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSizePolicy,
)
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from bluesky_widgets.qt.run_engine_client import QtRePlanQueue
from bluesky_queueserver_api import BPlan
from .base import PlanWidget


class ScanPlanWidget(PlanWidget):
    signal_update_motors = Signal(object)

    def __init__(self, model, parent=None):
        # Make this into a more general base, and then add variants on top of it, i.e,
        # relscan, grid_scan, etc
        super().__init__(model, parent)
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
        self.modifier_input_from = QLineEdit(self)
        self.modifier_input_from.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_from.setValidator(QDoubleValidator())
        self.modifier_input_to = QLineEdit(self)
        self.modifier_input_to.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_to.setValidator(QDoubleValidator())
        self.modifier_input_steps = QLineEdit(self)
        self.modifier_input_steps.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_steps.setValidator(QIntValidator())

        self.basePlanLayout.addWidget(self.noun_selection)
        self.basePlanLayout.addWidget(self.modifier_input_from)
        self.basePlanLayout.addWidget(self.modifier_input_to)
        self.basePlanLayout.addWidget(self.modifier_input_steps)

    def check_plan_ready(self):
        check1 = self.modifier_input_from.text() != ""
        check2 = self.modifier_input_to.text() != ""
        check3 = self.modifier_input_steps.text() != ""
        if check1 and check2 and check3:
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        start = float(self.modifier_input_from.text())
        end = float(self.modifier_input_to.text())
        steps = int(self.modifier_input_steps.text())
        item = BPlan("tes_scan", motor, start, end, steps)
        self.run_engine_client.queue_item_add(item=item)
