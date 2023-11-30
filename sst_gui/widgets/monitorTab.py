from qtpy.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from bluesky_widgets.qt.run_engine_client import (
    QtReEnvironmentControls,
    QtReManagerConnection,
    QtReStatusMonitor)
from .status import ProposalStatus, StatusBox, BLController
from .utils import HLine

"""
build monitor tab:
monitorTab(
    runEngine
    user_status
    sst_control
    ring_current -> ring_status_list
    gatevalves
    energy
    voltmeters
    manipulator
"""


class EnvironmentMonitor(QHBoxLayout):
    def __init__(self, run_engine, user_status, bl_control):
        super().__init__()
        self.addWidget(QtReManagerConnection(run_engine))
        self.addWidget(QtReStatusMonitor(run_engine))
        self.addWidget(QtReEnvironmentControls(run_engine))
        self.addWidget(ProposalStatus(run_engine, user_status))
        self.addWidget(BLController(bl_control))


class MonitorTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        t = (run_engine, user_status, controller,
        ring_status_list, gv_list, scalar_list, manipulator)
        vbox = QVBoxLayout()
        statusDisplay = EnvironmentMonitor(model.run_engine, model.user_status, model.bl_control)

        vbox.addLayout(statusDisplay)
        vbox.addWidget(HLine())

        beamBox = QHBoxLayout()
        beamBox.addWidget(PVMonitorBox(model.ringstatus))
        beamBox.addWidget(ShutterControlWidget(["psh7", "psh10", "psh4"]))
        beamBox.addWidget(autoloadEnergyMonitor(self.model.beamline))

        vbox.addLayout(beamBox)
        vbox.addWidget(HLine())

        vbox.addWidget(VoltMeterWidget(["sc", "i0", "ref"]))
        manipulator = findAndLoadDevice("manipulator")
        #vbox.addWidget(OphydPositionMonitor(eslit, "Exit Slit"))
        hbox = QHBoxLayout()
        hbox.addWidget(ManipulatorMonitor(manipulator))
        hbox.addWidget(StatusBox(user_status, "Selected Sample", "SAMPLE_SELECTED"))
        vbox.addLayout(hbox)
        vbox.addWidget(QtReRunningPlan(run_engine))
        vbox.addStretch()
        self.setLayout(vbox)
