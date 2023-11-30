

class SampleSelectWidget(QHBoxLayout):
    signal_update_widget = Signal(object)

    def __init__(self, run_engine, user_status, manipulator, *args, **kwargs):
        super().__init__()
        self.run_engine = run_engine
        self.addWidget(StatusBox(user_status, "Selected Sample", "SAMPLE_SELECTED"))
        self.signal_update_widget.connect(self.update_samples)
        user_status.register_signal("SAMPLE_LIST", self.signal_update_widget)

        vbox = QVBoxLayout()
        cb = QComboBox()
        gb = QGroupBox("Sample Selection")
        self.cb = cb
        self.cb2 = QComboBox()
        self.cb2.addItem("Center", "center")
        self.cb2.addItem("Edge", "edge")
        self.button = QPushButton("Move Sample")
        self.x = QLineEdit("0")
        self.y = QLineEdit("0")
        self.r = QLineEdit("45")

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
        gb.setLayout(vbox)
        self.addWidget(gb)
        self.addLayout(RealManipulatorMonitor(manipulator))

    def update_samples(self, samples):
        self.cb.clear()
        for key in samples.keys():
            self.cb.addItem(str(key), key)

    def select_sample(self):
        sample = self.cb.currentData()
        x = float(self.x.text())
        y = float(self.y.text())
        r = float(self.r.text())
        print((x, y, r))
        origin = self.cb2.currentData()
        plan = BPlan("sample_move", x, y, r, sample, origin=origin)
        self.run_engine._client.item_execute(plan)
