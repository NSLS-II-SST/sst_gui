from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
)
from .utils import ByteIndicator


class GVMonitor(QWidget):
    """
    Widget to monitor a GVModel, with an open/closed indicator
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(QLabel(model.label))
        self.indicator = ByteIndicator()
        self.model.gvStatusChanged.connect(self.update_indicator)
        self.vbox.addWidget(self.indicator)
        self.setLayout(self.vbox)

    def update_indicator(self, status):
        color = "green" if status == "open" else "red"
        self.indicator.setColor(color)


class GVControl(GVMonitor):
    """
    Widget to control a GVModel, with an open/closed indicator
    """

    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.opn = QPushButton("Open")
        self.opn.clicked.connect(self.model.open)
        self.close = QPushButton("Close")
        self.close.clicked.connect(self.model.close)
        self.vbox.insertWidget(1, self.opn)
        self.vbox.insertWidget(3, self.close)


class GVControlBox(QGroupBox):
    def __init__(self, shutters, *args, **kwargs):
        super().__init__("Shutter Control", *args, **kwargs)
        hbox = QHBoxLayout()
        for s in shutters:
            hbox.addWidget(GVControl(s))
        self.setLayout(hbox)
