from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox
from .motor import MotorMonitor, MotorControl


class RealManipulatorControl(QGroupBox):
    """
    Displays a group of real axis controls for a manipulator.

    Parameters
    ----------
    manipulator : object
        The manipulator model to display the real axis controls for.
    *args
        Variable length argument list.
    **kwargs
        Arbitrary keyword arguments.
    """

    def __init__(self, manipulator, *args, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Real Axes", *args, **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.real_axes_models:
            vbox.addWidget(MotorControl(m))
        self.setLayout(vbox)


class PseudoManipulatorControl(QGroupBox):
    def __init__(self, manipulator, *args, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Pseudoaxes", *args, **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.pseudo_axes_models:
            print(f"Adding {m.label} to PseudoManipulatorControl")
            vbox.addWidget(MotorControl(m))
        self.setLayout(vbox)


class RealManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Real Axes", *args, **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.real_axes_models:
            vbox.addWidget(MotorMonitor(m))
        self.setLayout(vbox)


class PseudoManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Pseudoaxes", *args, **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.pseudo_axes_models:
            vbox.addWidget(MotorMonitor(m))
        self.setLayout(vbox)


class ManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, *args, orientation=None, **kwargs):
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
