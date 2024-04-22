from qtpy.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QGroupBox,
    QPushButton,
    QLineEdit,
    QLabel,
)
from qtpy.QtCore import Signal, QObject
from .status import StatusBox
from .manipulator_monitor import RealManipulatorMonitor
from qtpy.QtGui import QDoubleValidator
from bluesky_queueserver_api import BPlan


class SampleSelectModel(QObject):
    signal_update_widget = Signal(object)
    signal_samples_updated = Signal(object)

    def __init__(self, run_engine, user_status, *args, **kwargs):
        super().__init__()
        self.run_engine = run_engine
        self.signal_update_widget.connect(self.update_samples)
        user_status.register_signal("SAMPLE_LIST", self.signal_update_widget)
        self.samples = {}
        self.currentSample = {}

    def update_samples(self, samples):
        self.samples = samples
        self.signal_samples_updated.emit(samples)

    def select_sample(self, sample, x, y, r, origin):
        plan = BPlan("sample_move", x, y, r, sample, origin=origin)
        return plan


class SampleSelectWidget(QGroupBox):
    def __init__(self, model, parent=None, **kwargs):
        super().__init__("Sample Selection", parent=parent)
        self.run_engine = model.run_engine
        self.model = SampleSelectModel(model.run_engine, model.user_status)
        self.model.signal_update_widget.connect(self.update_samples)

        vbox = QVBoxLayout()
        cb = QComboBox()
        self.cb = cb
        self.cb2 = QComboBox()
        self.cb2.addItem("Center", "center")
        self.cb2.addItem("Edge", "edge")
        self.button = QPushButton("Move Sample")
        self.x = QLineEdit("0")
        self.x.setValidator(QDoubleValidator())
        self.y = QLineEdit("0")
        self.y.setValidator(QDoubleValidator())
        self.r = QLineEdit("45")
        self.r.setValidator(QDoubleValidator())

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
        self.setLayout(vbox)

    def update_samples(self, samples):
        self.cb.clear()
        for k, v in samples.items():
            self.cb.addItem(f"Sample {k}: {v['name']}", k)

    def select_sample(self):
        sample = self.cb.currentData()
        x = float(self.x.text())
        y = float(self.y.text())
        r = float(self.r.text())
        print((x, y, r))
        origin = self.cb2.currentData()
        plan = BPlan("sample_move", x, y, r, sample, origin=origin)
        self.run_engine._client.item_execute(plan)
