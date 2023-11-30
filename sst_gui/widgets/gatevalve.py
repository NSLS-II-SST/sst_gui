from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QColor, QPushButton, QGroupBox)
from .utils import OphydByteIndicator
from ..models import OphydModel


class GVMonitor(QWidget):
    """
    Widget to monitor a GVModel, with an open/closed indicator
    """
    def __init__(self, model: OphydModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.obj = model.obj
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(model.label))
        self.indicator = OphydByteIndicator(self.obj.state)
        if self.obj.openval:
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
    def __init__(self, model: OphydModel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        vbox = QVBoxLayout()
        vbox.addWidget(QLabel(model.label))
        self.opn = QPushButton("Open")
        self.opn.clicked.connect(self.model.open)
        self.close = QPushButton("Close")
        self.close.clicked.connect(self.model.close)
        self.indicator = OphydByteIndicator(self.model.obj.state)
        if model.openval:
            self.indicator.setProperty("offColor", QColor(100, 100, 100))
            self.indicator.setProperty("onColor", QColor(0, 255, 0))
        else:
            self.indicator.setProperty("onColor", QColor(100, 100, 100))
            self.indicator.setProperty("offColor", QColor(0, 255, 0))
        self.indicator.setProperty("showLabels", False)
        vbox.addWidget(self.opn)
        vbox.addWidget(self.indicator)
        vbox.addWidget(self.close)
        self.setLayout(vbox)


class GVControlBox(QGroupBox):
    def __init__(self, shutters, *args, **kwargs):
        super().__init__("Shutter Control", *args, **kwargs)
        hbox = QHBoxLayout()
        for s in shutters:
            hbox.addWidget(GVControl(s))
        self.setLayout(hbox)
