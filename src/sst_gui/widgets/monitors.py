from qtpy.QtWidgets import QVBoxLayout, QWidget, QLabel, QHBoxLayout, QLineEdit, QPushButton


class PVControl(QWidget):
    def __init__(self, model, parent_model=None, orientation="v", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        if orientation == "v":
            box = QVBoxLayout()
        else:
            box = QHBoxLayout()
        self.label = model.label
        self.value = QLabel("")
        self.edit = QLineEdit("")
        self.model.valueChanged.connect(self.value.setText)
        self.setButton = QPushButton("Set")
        self.setButton.clicked.connect(self.enter_value)
        box.addWidget(QLabel(self.label))
        box.addWidget(self.value)
        box.addWidget(self.edit)
        box.addWidget(self.setButton)
        self.setLayout(box)

    def enter_value(self):
        val = float(self.edit.text())
        self.model.set(val)


class PVMonitor(QWidget):
    """
    Monitor a generic PV
    """

    def __init__(self, model, parent_model=None, orientation="v", **kwargs):
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
