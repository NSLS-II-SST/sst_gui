from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox, QWidget
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

    def __init__(self, manipulator, parent_model, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Real Axes", **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.real_axes_models:
            vbox.addWidget(MotorControl(m, parent_model))
        self.setLayout(vbox)


class PseudoManipulatorControl(QGroupBox):
    def __init__(self, manipulator, parent_model, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Pseudoaxes",**kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.pseudo_axes_models:
            print(f"Adding {m.label} to PseudoManipulatorControl")
            vbox.addWidget(MotorControl(m, parent_model))
        self.setLayout(vbox)


class RealManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, parent_model, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Real Axes", **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.real_axes_models:
            vbox.addWidget(MotorMonitor(m, parent_model))
        self.setLayout(vbox)


class PseudoManipulatorMonitor(QGroupBox):
    def __init__(self, manipulator, parent_model, orientation=None, **kwargs):
        super().__init__(manipulator.label + " Pseudoaxes", **kwargs)
        vbox = QVBoxLayout()
        for m in manipulator.pseudo_axes_models:
            vbox.addWidget(MotorMonitor(m, parent_model))
        self.setLayout(vbox)


class ManipulatorMonitor(QWidget):
    def __init__(self, manipulator, parent_model, orientation=None, parent=None, **kwargs):
        super().__init__(parent=parent)
        hbox = QHBoxLayout()
        hbox.addWidget(RealManipulatorMonitor(manipulator, parent_model, orientation, **kwargs))
        hbox.addWidget(PseudoManipulatorMonitor(manipulator, parent_model, orientation, **kwargs))
        self.setLayout(hbox)

class ManipulatorControl(QWidget):
    def __init__(self, manipulator, parent_model, orientation=None, parent=None, **kwargs):
        super().__init__(parent=parent)
        hbox = QHBoxLayout()
        hbox.addWidget(RealManipulatorControl(manipulator, parent_model, orientation, **kwargs))
        hbox.addWidget(PseudoManipulatorControl(manipulator, parent_model, orientation, **kwargs))
        self.setLayout(hbox)
