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
from .manipulator_monitor import RealManipulatorMonitor
from .energy import EnergyMonitor
from .views import AutoControl, AutoControlBox, AutoMonitor, AutoMonitorBox
from .motor import MotorControlCombo


class MotorTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # run_engine = model.run_engine
        # user_status = model.user_status
        beamline = model.beamline

        vbox = QVBoxLayout()

        vbox.addLayout(MotorControlCombo(beamline.motors))
        self.setLayout(vbox)
