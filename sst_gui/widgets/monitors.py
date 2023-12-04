from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout


class PVMonitorVBoxLayout(QVBoxLayout):
    def __init__(self, modeldict):
        super().__init__()
        for model in modeldict.values():
            self.addWidget(PVMonitor(model, "h"))


class PVMonitorHBoxLayout(QHBoxLayout):
    def __init__(self, modeldict):
        super().__init__()
        for model in modeldict.values():
            self.addWidget(PVMonitor(model, "v"))


class PVMonitor(QWidget):
    """
    Monitor a generic PV
    """

    def __init__(self, model, orientation="v", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        if orientation == "v":
            box = QVBoxLayout()
        else:
            box = QHBoxLayout()
        self.label = model.label
        self.value = QLabel("")
        self.model.valueChanged.connect(self.value.setText)
        box.addWidget(QLabel(self.label))
        box.addWidget(self.value)
        self.setLayout(box)


class PVMonitorV(PVMonitor):
    def __init__(self, model, **kwargs):
        super().__init__(model, orientation="v", **kwargs)


class PVMonitorH(PVMonitor):
    def __init__(self, model, **kwargs):
        super().__init__(model, orientation="h", **kwargs)
