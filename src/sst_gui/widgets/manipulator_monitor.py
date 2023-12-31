from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from .motor import MotorMonitor, MotorControl


class RealManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, **kwargs):
        super().__init__(manipulator.label, *args, **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.real_axes_models:
            vbox.addWidget(MotorMonitor(m))
        self.setLayout(vbox)


class ManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, **kwargs):
        super().__init__("Manipulator", *args, **kwargs)
        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox1.addWidget(MotorMonitor(manipulator.x))
        vbox1.addWidget(MotorMonitor(manipulator.y))
        vbox1.addWidget(MotorMonitor(manipulator.z))
        vbox1.addWidget(MotorMonitor(manipulator.r))
        vbox2 = QVBoxLayout()

        vbox2.addWidget(MotorControl(manipulator.sx))
        vbox2.addWidget(MotorMonitor(manipulator.sy))
        vbox2.addWidget(MotorMonitor(manipulator.sz))
        vbox2.addWidget(MotorMonitor(manipulator.sr))

        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        self.setLayout(hbox)
