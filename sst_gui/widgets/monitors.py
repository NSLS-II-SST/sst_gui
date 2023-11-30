class PVMonitorBoxLayout(QVBoxLayout):
    def __init__(self, modelList):
        super().__init__()
        for model in modelList:
            self.addWidget(PVMonitorV(model))


class PVMonitorV(QWidget):
    """
    Monitor a generic PV
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vbox = QVBoxLayout()
        self.label = model.label
        vbox.addWidget(QLabel(self.label))
        vbox.addWidget(PyDMLabel(init_channel=f"ca://{model.obj.pvname}"))
        self.setLayout(vbox)


class PVMonitorH(QWidget):
    """
    Monitor a generic PV
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hbox = QHBoxLayout()
        self.label = model.label
        hbox.addWidget(QLabel(f"{self.label}:"))
        hbox.addWidget(PyDMLabel(init_channel=f"ca://{model.obj.pvname}"))
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
