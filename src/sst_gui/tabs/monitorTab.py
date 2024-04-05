from qtpy.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from bluesky_widgets.qt.run_engine_client import (
    QtReExecutionControls,
    QtReQueueControls,
    QtReStatusMonitor,
    QtReRunningPlan,
)
from ..widgets.status import ProposalStatus, StatusBox, BLController
from ..widgets.utils import HLine
from ..widgets.manipulator_monitor import RealManipulatorControl, PseudoManipulatorControl
from ..widgets.views import AutoControl, AutoControlBox, AutoMonitor, AutoMonitorBox


class EnvironmentMonitor(QHBoxLayout):
    def __init__(self, run_engine, user_status, bl_control):
        super().__init__()
        self.addWidget(QtReStatusMonitor(run_engine))
        self.addWidget(QtReQueueControls(run_engine))
        self.addWidget(QtReExecutionControls(run_engine))
        self.addWidget(ProposalStatus(run_engine, user_status))
        self.addWidget(BLController(bl_control))


class MonitorTab(QWidget):
    name = "Beamline Status"

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

        beamBox.addWidget(AutoMonitorBox(beamline.signals, "Ring Signals", model, orientation='v'))
        print("Beamline signals box added")

        print("Beamline shutters box")
        beamBox.addWidget(AutoControlBox(beamline.shutters, "Shutters", model))
        print("Beamline shutters box added")

        beamBox.addWidget(PseudoManipulatorControl(beamline.primary_energy.energy, model))

        vbox.addLayout(beamBox)
        vbox.addWidget(HLine())

        vbox.addWidget(AutoMonitorBox(beamline.detectors, "Detectors", model, "h"))
        vbox.addWidget(AutoMonitorBox(beamline.vacuum, "Vacuum", model, "h"))
        print("Added detectors Monitor")
        hbox = QHBoxLayout()
        hbox.addWidget(RealManipulatorControl(beamline.primary_manipulator, model, orientation="v")
        )
        print("Added manipulator Monitor")

        hbox.addWidget(StatusBox(user_status, "Selected Sample", "SAMPLE_SELECTED"))
        vbox.addLayout(hbox)
        vbox.addWidget(QtReRunningPlan(run_engine))
        print("Added Running Plan Monitor")

        vbox.addStretch()
        self.setLayout(vbox)
