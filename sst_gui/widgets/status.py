from qtpy.QtWidgets import (QHBoxLayout, QWidget, QVBoxLayout, QGroupBox,
                            QLabel, QDialog, QLineEdit, QPushButton,
                            QFormLayout, QApplication)
from qtpy.QtCore import Signal, Slot
from pydm.widgets.pushbutton import PyDMPushButton
from pydm.widgets.label import PyDMLabel
from bluesky_queueserver_api import BFunc
from pydm.widgets.base import PyDMWidget


# TODO: Get rid of all pydm!
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


class StatusBox(QWidget):
    signal_update_widget = Signal(object)

    def __init__(self, status_model, title, key, parent=None):
        super().__init__(parent)
        self.model = status_model
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


class NewProposalDialog(QDialog):
    def __init__(self, title, run_engine):
        super().__init__()
        self.REClientModel = run_engine
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


class ProposalStatus(StatusBox):
    def __init__(self, run_engine, user_status):
        super().__init__(user_status, "User Metadata", "USER_MD")
        self.REClientModel = run_engine

        self.button = QPushButton("New Proposal")
        self.button.clicked.connect(self.push_button)
        self.vbox.addWidget(self.button)

    def push_button(self):
        dlg = NewProposalDialog("New Proposal", self.REClientModel)
        dlg.exec()


class BLController(QGroupBox):
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
