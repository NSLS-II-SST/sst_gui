from qtpy.QtWidgets import QWidget, QVBoxLayout, QLabel
from typhos.plugins import register_signal
from pydm.widgets.label import PyDMLabel

class TyphosSignalViewer(QWidget):
    def __init__(self, signal, label, *args, **kwargs):
        super().__init__(*args, **kwargs)
        register_signal(signal)
        vbox = QVBoxLayout()
        self.label = label
        vbox.addWidget(QLabel(self.label))
        vbox.addWidget(PyDMLabel(init_channel=f"sig://{signal.name}"))
        self.setLayout(vbox)
