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
    """
    GVControlBox is a widget that creates a view around GVModels.
    It takes a dictionary 'shutters' as an argument, where the values are GVModel objects.
    It provides a control interface for each GVModel in the 'shutters' dictionary.
    """

    def __init__(self, shutters, *args, **kwargs):
        """
        Initializes the GVControlBox widget.
        Args:
            shutters (dict): A dictionary where the values are GVModel objects.
            *args: Variable length argument list passed to the QGroupBox init method.
            **kwargs: Arbitrary keyword arguments passed to the QGroupBox init method.
        """
        super().__init__("Shutter Control", *args, **kwargs)
        print("In GVControlBox")
        hbox = QHBoxLayout()
        for s in shutters.values():
            hbox.addWidget(GVControl(s))
        self.setLayout(hbox)
