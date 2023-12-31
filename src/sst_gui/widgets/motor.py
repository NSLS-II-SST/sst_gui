from qtpy.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QVBoxLayout,
)
from qtpy.QtCore import Slot
from .utils import ByteIndicator


class MotorMonitor(QWidget):
    def __init__(self, model, orientation="h", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        if orientation == "h":
            self.box = QHBoxLayout()
        else:
            self.box = QVBoxLayout()
        self.label = QLabel(self.model.label)
        self.box.addWidget(self.label)
        self.position = QLabel("")
        self.box.addWidget(self.position)
        self.indicator = ByteIndicator()
        self.box.addWidget(self.indicator)
        self.model.valueChanged.connect(self.update_position)
        self.model.movingStatusChanged.connect(self.update_indicator)
        self.setLayout(self.box)

    @Slot(str)
    def update_position(self, value):
        self.position.setText(value)

    @Slot(bool)
    def update_indicator(self, status):
        color = "green" if status else "grey"
        self.indicator.setColor(color)


class MotorControl(MotorMonitor):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.lineEdit = QLineEdit()
        self.lineEdit.returnPressed.connect(self.enter_position)

        self.lineEdit.setText("{:2f}".format(self.model.setpoint.get()))
        self.box.insertWidget(2, self.lineEdit)
        lbutton = QPushButton("<")
        lbutton.clicked.connect(self.tweak_left)
        self.tweakEdit = QLineEdit()
        self.tweakEdit.setText("1")
        rbutton = QPushButton(">")
        rbutton.clicked.connect(self.tweak_right)
        self.box.insertWidget(4, lbutton)
        self.box.insertWidget(5, self.tweakEdit)
        self.box.insertWidget(6, rbutton)

    def enter_position(self):
        newpos = float(self.lineEdit.text())
        self.model.set(newpos)

    def tweak_left(self):
        current_sp = self.model.setpoint.get()
        step = float(self.tweakEdit.text())
        new_sp = current_sp - step
        self.model.set(new_sp)
        self.lineEdit.setText(str(new_sp))

    def tweak_right(self):
        current_sp = self.model.setpoint.get()
        step = float(self.tweakEdit.text())
        new_sp = current_sp + step
        self.model.set(new_sp)
        self.lineEdit.setText(str(new_sp))
