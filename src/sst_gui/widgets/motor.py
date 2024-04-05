from qtpy.QtWidgets import (
    QLabel,
    QPushButton,
    QHBoxLayout,
    QWidget,
    QLineEdit,
    QVBoxLayout,
    QComboBox,
    QStackedWidget,
)
from qtpy.QtCore import Slot, Qt
from .utils import SquareByteIndicator


class MotorMonitor(QWidget):
    def __init__(self, model, parent_model, orientation="h", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        if orientation == "h":
            self.box = QHBoxLayout()
        else:
            self.box = QVBoxLayout()
        if model.units is not None:
            self.units = model.units
        else:
            self.units = ""

        self.label = QLabel(self.model.label)
        self.box.addWidget(self.label)
        self.position = QLabel(self.model.value)
        print(self.model.label, self.model.value)
        self.box.addWidget(self.position)
        self.indicator = SquareByteIndicator()
        self.box.addWidget(self.indicator)
        if orientation == "h":
            self.box.setAlignment(Qt.AlignVCenter)
        self.model.valueChanged.connect(self.update_position)
        self.model.movingStatusChanged.connect(self.update_indicator)
        self.setLayout(self.box)

    @Slot(str)
    def update_position(self, value):
        self.position.setText(f"{value} {self.units}")

    @Slot(bool)
    def update_indicator(self, status):
        color = "green" if status else "grey"
        self.indicator.setColor(color)


class MotorControl(MotorMonitor):
    def __init__(self, model, *args, **kwargs):
        super().__init__(model, *args, **kwargs)
        self.lineEdit = QLineEdit()
        # self.lineEdit.returnPressed.connect(self.enter_position)

        self.lineEdit.setText("{:2f}".format(self.model.setpoint))
        self.model.setpointChanged.connect(self.update_sp)
        self.box.insertWidget(2, self.lineEdit)
        gobutton = QPushButton("Move")
        gobutton.clicked.connect(self.enter_position)
        lbutton = QPushButton("<")
        lbutton.clicked.connect(self.tweak_left)
        self.tweakEdit = QLineEdit()
        self.tweakEdit.setText("1")
        rbutton = QPushButton(">")
        rbutton.clicked.connect(self.tweak_right)
        stopButton = QPushButton("Stop!")
        stopButton.clicked.connect(self.model.stop)
        self.box.insertWidget(4, gobutton)
        self.box.insertWidget(5, lbutton)
        self.box.insertWidget(6, self.tweakEdit)
        self.box.insertWidget(7, rbutton)
        self.box.insertWidget(8, stopButton)

    def enter_position(self):
        newpos = float(self.lineEdit.text())
        self.model.set(newpos)

    def tweak_left(self):
        current_sp = self.model.setpoint
        step = float(self.tweakEdit.text())
        new_sp = current_sp - step
        self.model.set(new_sp)
        self.update_sp(new_sp)
        # self.lineEdit.setText(str(new_sp))

    def tweak_right(self):
        current_sp = self.model.setpoint
        step = float(self.tweakEdit.text())
        new_sp = current_sp + step
        self.model.set(new_sp)
        self.update_sp(new_sp)
        # self.lineEdit.setText(str(new_sp))

    def update_sp(self, value):
        if isinstance(value, (int, float)):
            self.lineEdit.setText("{:2f}".format(value))
        elif isinstance(value, str):
            self.lineEdit.setText(value)
        else:
            self.lineEdit.setText(str(value))
