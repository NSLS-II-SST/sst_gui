from bluesky_widgets.apps.queue_monitor.widgets import (
    QtRunEngineManager_Editor,
    QtRunEngineManager_Monitor,
)
from bluesky_queueserver_api import BPlan
from qtpy.QtWidgets import (
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QComboBox,
    QPushButton,
    QMessageBox,
)
from qtpy.QtCore import Signal
from pydm.widgets.label import PyDMLabel
from pydm.widgets.byte import PyDMByteIndicator
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.line_edit import PyDMLineEdit
from sst_funcs.configuration import findAndLoadDevice, getObjConfig
from .layout import FlowLayout
from ..models import energyModelFromOphyd, gvFromOphyd, motorFromOphyd
from .samplelist import QtSampleView
from ..tabs.monitorTab import MonitorTab

# from typhos.plugins import register_signal, SignalPlugin
# from typhos import TyphosPositionerWidget
# loadConfigDB("/home/xf07id1/nsls-ii-sst/ucal/ucal/object_config.yaml")
# pydm.data_plugins.add_plugin(SignalPlugin)


class EnergyMonitor(QGroupBox):
    """
    Display an Energy Model that has energy, gap, and phase
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__("Energy Monitor", *args, **kwargs)
        # vbox = QVBoxLayout()
        vbox = FlowLayout()
        vbox.addWidget(PVMonitorH(model.energy_RB, "PGM Energy"))
        vbox.addWidget(PVMonitorH(model.gap_RB, "Undulator Gap"))
        vbox.addWidget(PVMonitorH(model.phase_RB, "Undulator Phase"))
        vbox.addWidget(autoloadPVMonitor("Exit_Slit", "horizontal"))
        vbox.addWidget(PVMonitorH(model.grating_RB, "Grating"))
        self.setLayout(vbox)


class EnergyControl(QGroupBox):
    def __init__(self, model, *args, **kwargs):
        super().__init__("Energy Control", *args, **kwargs)
        energy = model.beamline.energy
        self.REClientModel = model.run_engine
        vbox = QVBoxLayout()
        vbox.addWidget(OphydMotorControl(energy.energy, "Energy"))
        vbox.addWidget(OphydMotorControl(model.beamline.eslit, "Exit Slit"))
        hbox = QHBoxLayout()
        hbox.addWidget(PVMonitorH(energy.monoen.gratingx.readback.pvname, "Grating"))
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


class TyphosSignalViewer(QWidget):
    def __init__(self, signal, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        register_signal(signal)
        vbox = QVBoxLayout()
        self.label = label
        vbox.addWidget(QLabel(self.label))
        vbox.addWidget(PyDMLabel(init_channel=f"sig://{signal.name}"))
        self.setLayout(vbox)


class RealManipulatorMonitor(QVBoxLayout):
    def __init__(self, manipulator):
        super().__init__()
        self.addWidget(MotorMonitor(manipulator.x))
        self.addWidget(MotorMonitor(manipulator.y))
        self.addWidget(MotorMonitor(manipulator.z))
        self.addWidget(MotorMonitor(manipulator.r))


class ManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, **kwargs):
        super().__init__("Manipulator", *args, **kwargs)
        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(MotorMonitor(manipulator.x))
        vbox1.addWidget(MotorMonitor(manipulator.y))
        vbox1.addWidget(MotorMonitor(manipulator.z))
        vbox1.addWidget(MotorMonitor(manipulator.r))
        vbox2 = QVBoxLayout()

        vbox2.addWidget(MotorControl(manipulator.sx))
        vbox2.addWidget(MotorMonitor(manipulator.sy))
        vbox2.addWidget(MotorMonitor(manipulator.sz))
        vbox2.addWidget(MotorMonitor(manipulator.sr))

        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        self.setLayout(hbox)


class MotorMonitor(PVMonitorH):
    def __init__(self, model):
        super().__init__(model.prefix, model.name)


class MotorControl(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QHBoxLayout()
        self.label = getattr(model, "display_name", model.name)

        indicator = PyDMByteIndicator(init_channel=f"ca://{model.prefix}.MOVN")
        indicator.setProperty("showLabels", False)

        stop = PyDMPushButton(init_channel=f"ca://{model.prefix}.STOP", label="STOP")
        stop.pressValue = 1

        hbox.addWidget(QLabel(self.label))
        hbox.addWidget(PyDMLineEdit(init_channel=f"ca://{model.prefix}.VAL"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{model.prefix}.RBV"))
        hbox.addWidget(indicator)
        hbox.addWidget(stop)
        self.setLayout(hbox)


def autoloadPVMonitor(name, orientation="vertical"):
    config = getObjConfig(name)
    print(config)
    if orientation == "vertical":
        return PVMonitorV(config["prefix"], config["name"])
    else:
        return PVMonitorH(config["prefix"], config["name"])


def loadOphydWidget(name, model, widget):
    oph = findAndLoadDevice(name)
    return widget(model(oph))


def autoloadVoltMonitor(name):
    config = getObjConfig(name)
    print(config)
    return VoltMonitor(config["prefix"], config["name"])


def autoloadGVMonitor(name):
    gv = gvFromOphyd(findAndLoadDevice(name))
    return GVMonitor(gv)


def autoloadGVControl(name):
    gv = gvFromOphyd(findAndLoadDevice(name))
    return GVControl(gv)


def autoloadMotorControl(name):
    mtr = motorFromOphyd(findAndLoadDevice(name))
    return MotorControl(mtr)


def autoloadEnergyMonitor(model):
    energy = energyModelFromOphyd(model.energy)
    return EnergyMonitor(energy)


class MotorSelectWidget(QVBoxLayout):
    signal_update_widget = Signal(object)

    def __init__(self, model, *args, **kwargs):
        super().__init__()
        self.model = model
        self.signal_update_widget.connect(self.update_motors)
        self.model.user_status.register_signal("MOTORS", self.signal_update_widget)

        cb = QComboBox()
        self.cb = cb

    def update_motors(self, samples):
        self.cb.clear()
        for key in samples.keys():
            self.cb.addItem(str(key), key)


class VoltMeterWidget(QGroupBox):
    def __init__(self, signals, *args, **kwargs):
        super().__init__("Voltmeters", *args, **kwargs)
        hbox = QHBoxLayout()
        for s in signals:
            hbox.addWidget(autoloadVoltMonitor(s))
        self.setLayout(hbox)


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.North)

        self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        self.addTab(self._re_manager_monitor, "Monitor Queue")

        self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        self.addTab(self._re_manager_editor, "Edit and Control Queue")

        self._bl_status_monitor = MonitorTab(model)
        self.addTab(self._bl_status_monitor, "Beamline Status")

        self._bl_interactive = InteractiveTab(model)
        self.addTab(self._bl_interactive, "Beamline Control")

        self._bl_sample_monitor = QtSampleView(model.user_status)
        self.addTab(self._bl_sample_monitor, "Samples")
