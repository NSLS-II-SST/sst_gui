from qtpy.QtWidgets import (
    QHBoxLayout,
    QWidget,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QDialog,
    QLineEdit,
    QPushButton,
    QFormLayout,
)
from qtpy.QtCore import Signal, Slot
from bluesky_queueserver_api import BFunc


class StatusBox(QGroupBox):
    signal_update_widget = Signal(object)

    def __init__(self, status_model, title, key, parent=None):
        super().__init__(title, parent)
        self.model = status_model
        self.signal_update_widget.connect(self.update_md)
        self.model.register_signal(key, self.signal_update_widget)
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

    @Slot(object)
    def update_md(self, user_md):
        items_in_layout = self.vbox.count()
        i = 0
        for k, v in user_md.items():
            if i + 1 > items_in_layout:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(str(k)))
                hbox.addWidget(QLabel(str(v)))
                self.vbox.addLayout(hbox)
            else:
                hbox = self.vbox.itemAt(i)
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
        self.model = model
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(""))
        onbutton = QPushButton("Request Control")
        self.onValue = 4
        onbutton.showConfirmDialog = True
        onbutton.confirmMessage = "Are you sure you can have control?"
        offbutton = QPushButton("Give Up Control")
        self.offValue = 9
        offbutton.showConfirmDialog = True
        offbutton.confirmMessage = "Are you sure you want to release control?"

        vbox.addWidget(onbutton)
        vbox.addWidget(offbutton)
        self.setLayout(vbox)

    def print_disable():
        print("Disabled in SST Control")
