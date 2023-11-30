from pydm import PyDMByteIndicator
from qtpy.QtWidgets import QFrame


class HLine(QFrame):
    """
    Creates a horizontal separator line
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


def OphydByteIndicator(ophSignal):
    pv = ophSignal.pvname
    return PyDMByteIndicator(init_channel=f"ca://{pv}")
