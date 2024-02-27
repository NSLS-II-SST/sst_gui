from qtpy.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QStackedWidget,
    QComboBox,
    QLabel,
)

from .status import ProposalStatus, StatusBox, BLController
from .utils import HLine
from .monitors import PVMonitorVBoxLayout, PVMonitorHBoxLayout
from .gatevalve import GVControlBox
from .manipulator_monitor import RealManipulatorControl, PseudoManipulatorControl
from .energy import EnergyControl, EnergyMonitor
from .views import AutoControl, AutoControlBox, AutoMonitor, AutoMonitorBox
from .motor import MotorControlCombo


class MotorTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # run_engine = model.run_engine
        # user_status = model.user_status
        beamline = model.beamline

        vbox = QVBoxLayout()
        vbox.addWidget(GVControlBox(beamline.shutters))
        vbox.addWidget(MotorControlCombo(beamline.motors))
        vbox.addWidget(EnergyControl(model))
        hbox = QHBoxLayout()
        print("Real Manipulator")
        hbox.addWidget(RealManipulatorControl(beamline.manipulators["manipulator"]))
        print("Pseudo Manipulator")
        hbox.addWidget(PseudoManipulatorControl(beamline.manipulators["manipulator"]))
        vbox.addLayout(hbox)
        vbox.addStretch()
        self.setLayout(vbox)
