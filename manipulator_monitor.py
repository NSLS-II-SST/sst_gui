from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from ..layout import FlowLayout
from .monitorTab import MotorMonitor, MotorControl

class RealManipulatorMonitor(QVBoxLayout):
    def __init__(self, manipulator):
        super().__init__()
        self.addWidget(MotorMonitor(manipulator.x))
        self.addWidget(MotorMonitor(manipulator.y))
        self.addWidget(MotorMonitor(manipulator.z))
        self.addWidget(MotorMonitor(manipulator.r))


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
