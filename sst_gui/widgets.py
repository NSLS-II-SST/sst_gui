from bluesky_widgets.apps.queue_monitor.widgets import (
    QtRunEngineManager_Editor,
    QtRunEngineManager_Monitor,
)
from bluesky_widgets.qt.threading import FunctionWorker
from bluesky_widgets.qt.run_engine_client import (
    QtReEnvironmentControls,
    QtReManagerConnection,
    QtReQueueControls,
    QtReExecutionControls,
    QtReStatusMonitor,
    QtRePlanQueue,
    QtRePlanHistory,
    QtReRunningPlan,
    QtRePlanEditor,
    QtReConsoleMonitor,
)
from bluesky_queueserver_api import BPlan, BFunc
from qtpy.QtWidgets import (QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QFrame, QGroupBox, QApplication, QLineEdit,
                            QComboBox, QPushButton, QMessageBox, QDialog,
                            QDialogButtonBox, QFormLayout
                            )
from qtpy.QtCore import Signal, Slot
from qtpy.QtGui import QColor
from pydm.widgets.label import PyDMLabel
from pydm.widgets.byte import PyDMByteIndicator
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.line_edit import PyDMLineEdit
from pydm.widgets.enum_combo_box import PyDMEnumComboBox
from pydm.widgets.base import PyDMWidget
import pydm
from sst_funcs.configuration import loadConfigDB, findAndLoadDevice, getObjConfig
from .layout import FlowLayout
from .models import energyModelFromOphyd, gvFromOphyd, motorFromOphyd, pvFromOphyd
from .samplelist import QtSampleView
from typhos.plugins import register_signal, SignalPlugin
#from typhos import TyphosPositionerWidget
loadConfigDB("/home/jamie/work/nsls-ii-sst/ucal/ucal/sim_config.yaml")
#pydm.data_plugins.add_plugin(SignalPlugin)


class HLine(QFrame):
    """
    Creates a horizontal separator line
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class EnergyMonitor(QGroupBox):
    """
    Display an Energy Model that has energy, gap, and phase
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__("Energy Monitor", *args, **kwargs)
        #vbox = QVBoxLayout()
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


class GVMonitor(QWidget):
    """
    Widget to monitor a GVModel, with an open/closed indicator
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(model.name))
        self.indicator = PyDMByteIndicator(init_channel=f"ca://{model.state_RB}")
        if model.openval:
            self.indicator.setProperty("offColor", QColor(100, 100, 100))
            self.indicator.setProperty("onColor", QColor(0, 255, 0))
        else:
            self.indicator.setProperty("onColor", QColor(100, 100, 100))
            self.indicator.setProperty("offColor", QColor(0, 255, 0))
        self.indicator.setProperty("showLabels", False)
        vbox.addWidget(self.indicator)
        self.setLayout(vbox)


class GVControl(QWidget):
    """
    Widget to control a GVModel, with an open/closed indicator
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(model.name))
        opn = PyDMPushButton(init_channel=f"ca://{model.cmd_open}", label="Open")
        opn.pressValue = 1
        close = PyDMPushButton(init_channel=f"ca://{model.cmd_close}", label="Close")
        close.pressValue = 1
        self.indicator = PyDMByteIndicator(init_channel=f"ca://{model.state_RB}")
        if model.openval:
            self.indicator.setProperty("offColor", QColor(100, 100, 100))
            self.indicator.setProperty("onColor", QColor(0, 255, 0))
        else:
            self.indicator.setProperty("onColor", QColor(100, 100, 100))
            self.indicator.setProperty("offColor", QColor(0, 255, 0))
        self.indicator.setProperty("showLabels", False)
        vbox.addWidget(opn)
        vbox.addWidget(self.indicator)
        vbox.addWidget(close)
        self.setLayout(vbox)


class OphydMotorViewer(QWidget):
    position_updated = Signal(float)

    def __init__(self, signal, label=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        box = QHBoxLayout()
        if label is None:
            label = getattr(signal, "display_name", signal.name)
        self.label = QLabel(label)
        box.addWidget(self.label)
        self.position = QLabel("")
        box.addWidget(self.position)
        signal.subscribe(self._update_position)
        self.position_updated.connect(self.update_position)
        self.setLayout(box)

    def _update_position(self, *args, value, **newpos):
        self.position_updated.emit(value)

    @Slot(float)
    def update_position(self, value):
        self.position.setText(str(value))


class OphydMotorControl(QWidget):
    position_updated = Signal(float)

    def __init__(self, signal, label=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        box = QHBoxLayout()
        self.signal = signal
        if label is None:
            label = getattr(signal, "display_name", signal.name)
        self.label = QLabel(label)
        box.addWidget(self.label)
        self.lineEdit = QLineEdit()
        self.lineEdit.editingFinished.connect(self.enter_position)
        if hasattr(signal, "setpoint"):
            self.setpoint = signal.setpoint
        else:
            self.setpoint = signal.user_setpoint
        self.lineEdit.setText(str(self.setpoint.get()))
        box.addWidget(self.lineEdit)
        self.position = QLabel("")
        box.addWidget(self.position)
        signal.subscribe(self._update_position)
        self.position_updated.connect(self.update_position)
        lbutton = QPushButton("<")
        lbutton.clicked.connect(self.tweak_left)
        self.tweakEdit = QLineEdit()
        self.tweakEdit.setText("1")
        rbutton = QPushButton(">")
        rbutton.clicked.connect(self.tweak_right)
        box.addWidget(lbutton)
        box.addWidget(self.tweakEdit)
        box.addWidget(rbutton)
        self.setLayout(box)

    def _update_position(self, *args, value, **newpos):
        self.position_updated.emit(value)

    @Slot(float)
    def update_position(self, value):
        self.position.setText(str(value))

    def enter_position(self):
        newpos = float(self.lineEdit.text())
        self.signal.set(newpos)

    def tweak_left(self):
        current_position = self.signal.position
        step = float(self.tweakEdit.text())
        new_sp = current_position - step
        self.signal.set(new_sp)
        self.lineEdit.setText(str(new_sp))

    def tweak_right(self):
        current_position = self.signal.position
        step = float(self.tweakEdit.text())
        new_sp = current_position + step
        self.signal.set(new_sp)
        self.lineEdit.setText(str(new_sp))


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

        vbox2.addWidget(OphydMotorControl(manipulator.sx))
        vbox2.addWidget(OphydMotorViewer(manipulator.sy))
        vbox2.addWidget(OphydMotorViewer(manipulator.sz))
        vbox2.addWidget(OphydMotorViewer(manipulator.sr))

        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        self.setLayout(hbox)


class PVMonitorV(QWidget):
    """
    Monitor a generic PV
    """
    def __init__(self, prefix, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        self.label = label
        vbox.addWidget(QLabel(self.label))
        vbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}"))
        self.setLayout(vbox)


class PVMonitorH(QWidget):
    """
    Monitor a generic PV
    """
    def __init__(self, prefix, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QHBoxLayout()
        self.label = label
        hbox.addWidget(QLabel(f"{self.label}:"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}"))
        self.setLayout(hbox)


class VoltMonitor(QWidget):
    """
    Monitor a generic PV
    """
    def __init__(self, prefix, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        self.label = label
        vbox.addWidget(QLabel(self.label))
        vbox.addWidget(PyDMLabel(init_channel=f"ca://{prefix}Volt"))
        self.setLayout(vbox)


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


class PyDMDisabler(QWidget, PyDMWidget):
    disableSignal = Signal()

    def __init__(self, parent=None, init_channel=None):
        QWidget.__init__(self, parent)
        PyDMWidget.__init__(self, init_channel=init_channel)
        self.app = QApplication.instance()

    def value_changed(self, new_value):
        if new_value != 4:
            print("Disable!")
            self.disableSignal.emit()


class SSTControl(QGroupBox):
    disableSignal = Signal()

    def __init__(self, model, *args, **kwargs):
        super().__init__("Endstation Control", *args, **kwargs)
        self.disabler = PyDMDisabler(init_channel=f"ca://{model.prefix}")
        vbox = QVBoxLayout()
        vbox.addWidget(PyDMLabel(init_channel=f"ca://{model.prefix}"))
        onbutton = PyDMPushButton(init_channel=f"ca://{model.prefix}",
                                  label="Request Control")
        onbutton.pressValue = 4
        onbutton.showConfirmDialog = True
        onbutton.confirmMessage = "Are you sure you can have control?"
        offbutton = PyDMPushButton(init_channel=f"ca://{model.prefix}",
                                   label="Give Up Control")
        offbutton.pressValue = 9
        offbutton.showConfirmDialog = True
        offbutton.confirmMessage = "Are you sure you want to release control?"

        vbox.addWidget(onbutton)
        vbox.addWidget(offbutton)
        self.setLayout(vbox)

    def print_disable():
        print("Disabled in SST Control")


def autoloadPVMonitor(name, orientation="vertical"):
    config = getObjConfig(name)
    print(config)
    if orientation == "vertical":
        return PVMonitorV(config['prefix'], config['name'])
    else:
        return PVMonitorH(config['prefix'], config['name'])


def loadOphydWidget(name, model, widget):
    oph = findAndLoadDevice(name)
    return widget(model(oph))


def autoloadVoltMonitor(name):
    config = getObjConfig(name)
    print(config)
    return VoltMonitor(config['prefix'], config['name'])


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


class FormDialog(QDialog):
    def __init__(self, title, model):
        super().__init__()
        self.REClientModel = model
        self.setWindowTitle(title)
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel("Test!"))
        button = QPushButton("Submit")
        button.clicked.connect(self.submit_form)
        form = QFormLayout()
        self.name = QLineEdit()
        self.SAF = QLineEdit()
        self.proposal = QLineEdit()
        self.cycle = QLineEdit()
        self.year = QLineEdit()
        form.addRow("Name", self.name)
        form.addRow("proposal", self.proposal)
        form.addRow("SAF", self.SAF)
        form.addRow("Cycle", self.cycle)
        form.addRow("Year", self.year)
        vbox.addLayout(form)
        vbox.addWidget(button)
        self.setLayout(vbox)

    def submit_form(self):
        names = self.name.text()
        proposal = int(self.proposal.text())
        saf = int(self.SAF.text())
        cycle = int(self.cycle.text())
        year = int(self.year.text())
        function = BFunc("new_proposal", names, proposal, year, cycle, saf)
        self.REClientModel._client.function_execute(function)


class QtStatusBox(QWidget):
    signal_update_widget = Signal(object)

    def __init__(self, model, title, key, parent=None):
        super().__init__(parent)
        self.model = model
        self.signal_update_widget.connect(self.update_md)
        self.model.register_signal(key, self.signal_update_widget)
        self._group_box = QGroupBox(title)
        self.vbox = QVBoxLayout()
        self.vbox2 = QVBoxLayout()
        self._group_box.setLayout(self.vbox2)
        self.vbox.addWidget(self._group_box)
        self.setLayout(self.vbox)

    @Slot(object)
    def update_md(self, user_md):
        items_in_layout = self.vbox2.count()
        i = 0
        for k, v in user_md.items():
            if i+1 > items_in_layout:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(str(k)))
                hbox.addWidget(QLabel(str(v)))
                self.vbox2.addLayout(hbox)
            else:
                hbox = self.vbox2.itemAt(i)
                key = hbox.itemAt(0).widget()
                val = hbox.itemAt(1).widget()
                key.setText(str(k))
                val.setText(str(v))
            i += 1


class ProposalStatus(QtStatusBox):
    def __init__(self, model):
        super().__init__(model.user_status, "User Metadata", "USER_MD")
        self.REClientModel = model.run_engine

        self.button = QPushButton("New Proposal")
        self.button.clicked.connect(self.push_button)
        self.vbox.addWidget(self.button)

    def push_button(self):
        dlg = FormDialog("New Proposal", self.REClientModel)
        dlg.exec()


class SSTMonitorTab(QWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        statusBox = QHBoxLayout()
        statusBox.addWidget(QtReManagerConnection(model.run_engine))
        statusBox.addWidget(QtReStatusMonitor(model.run_engine))
        statusBox.addWidget(QtReEnvironmentControls(model.run_engine))
        #statusBox.addWidget(QtStatusBox(model.user_status, "User Metadata", "USER_MD"))
        statusBox.addWidget(ProposalStatus(model))

        controller = loadOphydWidget("sst_control", pvFromOphyd, SSTControl)
        controller.disabler.disableSignal.connect(self.print_disabled)
        statusBox.addWidget(controller)
        vbox.addLayout(statusBox)
        vbox.addWidget(HLine())

        beamBox = QHBoxLayout()
        beamBox.addWidget(autoloadPVMonitor("ring_current"))
        beamBox.addWidget(ShutterControlWidget(["psh7", "psh10", "psh4"]))
        beamBox.addWidget(autoloadEnergyMonitor(self.model.beamline))

        vbox.addLayout(beamBox)
        vbox.addWidget(HLine())

        vbox.addWidget(VoltMeterWidget(["sc", "i0", "i1", "ref"]))
        manipulator = findAndLoadDevice("manipulator")
        #vbox.addWidget(OphydPositionMonitor(eslit, "Exit Slit"))
        hbox = QHBoxLayout()
        hbox.addWidget(ManipulatorMonitor(manipulator))
        hbox.addWidget(QtStatusBox(model.user_status, "Selected Sample", "SAMPLE_SELECTED"))
        vbox.addLayout(hbox)
        vbox.addWidget(QtReRunningPlan(model.run_engine))
        vbox.addStretch()
        self.setLayout(vbox)

    def print_disabled(self):
        print("Disabled at top level")


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


class SampleSelectWidget(QHBoxLayout):
    signal_update_widget = Signal(object)

    def __init__(self, model, *args, **kwargs):
        super().__init__()
        self.model = model
        self.addWidget(QtStatusBox(model.user_status, "Selected Sample", "SAMPLE_SELECTED"))
        self.signal_update_widget.connect(self.update_samples)
        self.model.user_status.register_signal("SAMPLE_LIST", self.signal_update_widget)

        vbox = QVBoxLayout()
        cb = QComboBox()
        gb = QGroupBox("Sample Selection")
        self.cb = cb
        self.cb2 = QComboBox()
        self.cb2.addItem("Center", "center")
        self.cb2.addItem("Edge", "edge")
        self.button = QPushButton("Move Sample")
        self.x = QLineEdit("0")
        self.y = QLineEdit("0")
        self.r = QLineEdit("45")

        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("x"))
        hbox.addWidget(self.x)
        hbox.addWidget(QLabel("y"))
        hbox.addWidget(self.y)
        hbox.addWidget(QLabel("r"))
        hbox.addWidget(self.r)
        self.button.clicked.connect(self.select_sample)
        vbox.addWidget(self.cb)
        vbox.addLayout(hbox)
        vbox.addWidget(self.cb2)
        vbox.addWidget(self.button)
        gb.setLayout(vbox)
        self.addWidget(gb)
        self.addLayout(RealManipulatorMonitor(model.beamline.manipulator))

    def update_samples(self, samples):
        self.cb.clear()
        for key in samples.keys():
            self.cb.addItem(str(key), key)

    def select_sample(self):
        sample = self.cb.currentData()
        x = float(self.x.text())
        y = float(self.y.text())
        r = float(self.r.text())
        print((x, y, r))
        origin = self.cb2.currentData()
        plan = BPlan("sample_move", x, y, r, sample, origin=origin)
        self.model.run_engine._client.item_execute(plan)


class ShutterControlWidget(QGroupBox):
    def __init__(self, shutters, *args, **kwargs):
        super().__init__("Shutter Control", *args, **kwargs)
        #flow = FlowLayout()
        hbox = QHBoxLayout()
        for s in shutters:
            hbox.addWidget(autoloadGVControl(s))
        self.setLayout(hbox)


class VoltMeterWidget(QGroupBox):
    def __init__(self, signals, *args, **kwargs):
        super().__init__("Voltmeters", *args, **kwargs)
        hbox = QHBoxLayout()
        for s in signals:
            hbox.addWidget(autoloadVoltMonitor(s))
        self.setLayout(hbox)


class InteractiveTab(QWidget):

    def __init__(self, model, *args, **kwargs):
        print("Initializing Placeholder Tab")
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(autoloadPVMonitor("ring_current"))
        hbox.addWidget(VoltMeterWidget(["sc", "i0", "i1", "ref"]))
        vbox.addLayout(hbox)
        #self.controller = loadOphydWidget("sst_control", pvFromOphyd, SSTControl)
        #self.controller.disabler.disableSignal.connect(self.print_disabled)
        #vbox.addWidget(self.controller)
        vbox.addWidget(ShutterControlWidget(["psh7", "psh10", "psh4"]))
        vbox.addWidget(HLine())
        vbox.addWidget(EnergyControl(model))
        vbox.addWidget(autoloadMotorControl("tesz"))
        vbox.addWidget(autoloadMotorControl("i0upAu"))
        vbox.addLayout(SampleSelectWidget(model))
        vbox.addStretch()
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QtStatusBox(model.user_status, "User Metadata", "USER_MD"))
        hbox2.addWidget(QtStatusBox(model.user_status, "Selected Sample", "SAMPLE_SELECTED"))
        #hbox.addWidget(QtStatusBox(model.user_status, "Sample List", "SAMPLE_LIST"))
        vbox.addLayout(hbox2)
        self.setLayout(vbox)

    def print_disabled(self):
        print("Disabled at top level")


class QtViewer(QTabWidget):
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model

        self.setTabPosition(QTabWidget.North)

        self._re_manager_monitor = QtRunEngineManager_Monitor(model.run_engine)
        self.addTab(self._re_manager_monitor, "Monitor Queue")

        self._re_manager_editor = QtRunEngineManager_Editor(model.run_engine)
        self.addTab(self._re_manager_editor, "Edit and Control Queue")

        self._bl_status_monitor = SSTMonitorTab(model)
        self.addTab(self._bl_status_monitor, "Beamline Status")

        self._bl_interactive = InteractiveTab(model)
        self.addTab(self._bl_interactive, "Beamline Control")

        self._bl_sample_monitor = QtSampleView(model.user_status)
        self.addTab(self._bl_sample_monitor, "Samples")
