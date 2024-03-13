from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from .motor import MotorMonitor, MotorControl

from bluesky_queueserver_api import BPlan


class EnergyMonitor(QGroupBox):
    """
    Display an Energy Model that has energy, gap, and phase
    """

    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        super().__init__("Energy Monitor", *args, **kwargs)
        vbox = QVBoxLayout()
        vbox.addWidget(MotorMonitor(energy.energy_motor, parent_model))
        vbox.addWidget(MotorMonitor(energy.gap_motor, parent_model))
        vbox.addWidget(MotorMonitor(energy.phase_motor, parent_model))
        vbox.addWidget(
            MotorMonitor(parent_model.beamline.motors["Exit_Slit"], parent_model)
        )
        vbox.addWidget(MotorMonitor(energy.grating_motor, parent_model))
        self.setLayout(vbox)


class EnergyControl(QGroupBox):
    def __init__(self, energy, parent_model, *args, orientation=None, **kwargs):
        super().__init__("Energy Control", *args, **kwargs)

        print(energy)
        self.REClientModel = parent_model.run_engine
        print("Creating Energy Control Vbox")
        vbox = QVBoxLayout()
        print("Creating Energy Motor")
        vbox.addWidget(MotorControl(energy.energy_motor, parent_model))
        print("Creating Exit Slit")
        vbox.addWidget(
            MotorControl(parent_model.beamline.motors["Exit_Slit"], parent_model)
        )
        print("Making hbox")
        hbox = QHBoxLayout()
        hbox.addWidget(MotorMonitor(energy.grating_motor, parent_model))
        print("Making ComboBox")
        cb = QComboBox()
        self.cb = cb
        cb.addItem("250 l/mm", 2)
        cb.addItem("1200 l/mm", 9)
        self.button = QPushButton("Change Grating")
        self.button.clicked.connect(self.change_grating)
        hbox.addWidget(cb)
        hbox.addWidget(self.button)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def change_grating(self):
        enum = self.cb.currentData()
        print(enum)
        if self.confirm_dialog():
            if enum == 9:
                plan = BPlan("base_grating_to_1200")
            else:
                plan = BPlan("base_grating_to_250")
            self.REClientModel._client.item_execute(plan)

    def confirm_dialog(self):
        """
        Show the confirmation dialog with the proper message in case
        ```showConfirmMessage``` is True.

        Returns
        -------
        bool
            True if the message was confirmed or if ```showCofirmMessage```
            is False.
        """

        confirm_message = "Are you sure you want to change gratings?"
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)

        msg.setText(confirm_message)

        # Force "Yes" button to be on the right (as on macOS) to follow common design practice
        msg.setStyleSheet("button-layout: 1")  # MacLayout

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        ret = msg.exec_()
        if ret == QMessageBox.No:
            return False
        return True
