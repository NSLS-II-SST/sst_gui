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


class MovePlanWidget(PlanWidget):
    signal_update_motors = Signal(object)
    modifiersAllowed = []

    def __init__(self, model, parent=None):
        super().__init__(model, parent, position=float)
        print("Initializing Move")
        self.display_name = "move"
        self.motors = {}

        self.user_status.register_signal(
            "MOTOR_DESCRIPTIONS", self.signal_update_motors
        )
        self.create_move_modifier()
        self.signal_update_motors.connect(self.update_motors)
        print("Move Initialized")
        # Create and add the move related widgets here

    def update_motors(self, plan_dict):
        inverted_dict = {}
        for key, value in plan_dict.items():
            if value != "":
                inverted_dict[value] = key
        self.motors = inverted_dict
        self.noun_selection.clear()
        self.noun_selection.addItems(self.motors.keys())
        print(plan_dict)

    def create_move_modifier(self):
        self.noun_selection = QComboBox(self)
        self.noun_selection.addItems(self.motors.keys())
        self.basePlanLayout.addWidget(self.noun_selection)

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        params = self.get_params()
        item = BPlan("move", motor, params["position"])
        self.run_engine_client.queue_item_add(item=item)
