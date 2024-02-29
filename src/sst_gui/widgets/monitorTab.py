from qtpy.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from bluesky_widgets.qt.run_engine_client import (
    QtReExecutionControls,
    QtReQueueControls,
    QtReStatusMonitor,
    QtReRunningPlan,
)
from .status import ProposalStatus, StatusBox, BLController
from .utils import HLine
from .monitors import PVMonitorVBoxLayout, PVMonitorHBoxLayout
from .gatevalve import GVControlBox
from .manipulator_monitor import RealManipulatorMonitor
from .energy import EnergyMonitor
from .views import AutoControl, AutoControlBox, AutoMonitor, AutoMonitorBox


class EnvironmentMonitor(QHBoxLayout):
    def __init__(self, run_engine, user_status, bl_control):
        super().__init__()
        self.addWidget(QtReStatusMonitor(run_engine))
        self.addWidget(QtReQueueControls(run_engine))
        self.addWidget(QtReExecutionControls(run_engine))
        self.addWidget(ProposalStatus(run_engine, user_status))
        self.addWidget(BLController(bl_control))


class MonitorTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        run_engine = model.run_engine
        user_status = model.user_status
        beamline = model.beamline
        vbox = QVBoxLayout()
        print("Adding Environment Monitor")
        statusDisplay = EnvironmentMonitor(
            run_engine, user_status, beamline.signals["sst_control"]
        )

        vbox.addLayout(statusDisplay)
        vbox.addWidget(HLine())
        beamBox = QHBoxLayout()
        print("Creating Beamline signals box")

        beamBox.addWidget(AutoMonitorBox(beamline.signals, "Ring Signals"))
        print("Beamline signals box added")

        print("Beamline shutters box")
        beamBox.addWidget(AutoControlBox(beamline.shutters, "Shutters"))
        print("Beamline shutters box added")

        beamBox.addWidget(EnergyMonitor(beamline.energy, beamline.motors["Exit_Slit"]))

        vbox.addLayout(beamBox)
        vbox.addWidget(HLine())

        vbox.addWidget(AutoMonitorBox(beamline.detectors, "Detectors", "h"))
        print("Added detectors Monitor")
        hbox = QHBoxLayout()
        hbox.addWidget(RealManipulatorMonitor(beamline.manipulators["manipulator"]))
        print("Added manipulator Monitor")

        hbox.addWidget(StatusBox(user_status, "Selected Sample", "SAMPLE_SELECTED"))
        vbox.addLayout(hbox)
        vbox.addWidget(QtReRunningPlan(run_engine))
        print("Added Running Plan Monitor")

        vbox.addStretch()
        self.setLayout(vbox)
