from bluesky_widgets.apps.queue_monitor.widgets import (
    QtRunEngineManager_Editor,
    QtRunEngineManager_Monitor,
)
from qtpy.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from qtpy.QtCore import Signal
from qtpy.QtGui import QColor
from pydm.widgets.label import PyDMLabel
from pydm.widgets.byte import PyDMByteIndicator
from sst_funcs.configuration import loadConfigDB, findAndLoadDevice, getObjConfig
from .layout import FlowLayout

loadConfigDB("/home/jamie/work/nsls-ii-sst/ucal/ucal/sim_config.yaml")


class HLine(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)

class MockEnergyMonitor(QWidget):
    def __init__(self, prefix, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix = prefix
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("PGM Energy"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}MonoMtr.RBV"))
        hbox.addWidget(QLabel("Undulator Gap"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}GapMtr.RBV"))
        hbox.addWidget(QLabel("Undulator Phase"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}PhaseMtr.RBV"))
        self.setLayout(hbox)


class GVMonitor(QWidget):
    def __init__(self, prefix, label, *args, openval=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.openval = openval
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel(label))
        self.indicator = PyDMByteIndicator(init_channel=f"ca://{prefix}Pos-Sts")
        if openval:
            self.indicator.setProperty("onColor", QColor(100, 100, 100))
            self.indicator.setProperty("offColor", QColor(0, 255, 0))
        else:
            self.indicator.setProperty("offColor", QColor(100, 100, 100))
            self.indicator.setProperty("onColor", QColor(0, 255, 0))
        self.indicator.setProperty("showLabels", False)
        hbox.addWidget(self.indicator)
        self.setLayout(hbox)


class PVMonitor(QWidget):
    def __init__(self, prefix, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QHBoxLayout()
        self.label = label
        hbox.addWidget(QLabel(self.label))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}"))
        self.setLayout(hbox)


def autoloadPVMonitor(name):
    config = getObjConfig(name)
    print(config)
    return PVMonitor(config['prefix'], config['name'])


def autoloadGVMonitor(name):
    config = getObjConfig(name)
    return GVMonitor(config['prefix'], config['name'])


class QtPlaceholder(QWidget):
    def __init__(self, *args, **kwargs):
        print("Initializing Placeholder Tab")
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        vbox.addWidget(autoloadPVMonitor("ring_current"))
        flow = FlowLayout()
        flow.addWidget
        flow.addWidget(autoloadGVMonitor("psh7"))
        flow.addWidget(autoloadGVMonitor("psh10"))
        flow.addWidget(autoloadGVMonitor("psh4"))
        vbox.addLayout(flow)
        vbox.addWidget(HLine())
        vbox.addWidget(MockEnergyMonitor("SIM_SST:energy:"))
        vbox.addStretch()
        self.setLayout(vbox)


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.West)

        self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        self.addTab(self._re_manager_monitor, "Monitor Queue")

        self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        self.addTab(self._re_manager_editor, "Edit and Control Queue")

        self._bl_status_monitor = QtPlaceholder()
        self.addTab(self._bl_status_monitor, "Beamline Status")
