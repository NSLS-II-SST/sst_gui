from qtpy.QtWidgets import QLabel, QPushButton, QHBoxLayout, QWidget, QLineEdit
from qtpy.QtCore import Signal, Slot
from .utils import OphydByteIndicator


class MotorMonitor(QWidget):
    position_updated = Signal(float)

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        box = QHBoxLayout()
        self.label = QLabel(self.model.label)
        box.addWidget(self.label)
        self.position = QLabel("")
        box.addWidget(self.position)
        box.addWidget(OphydByteIndicator(self.obj.motor_is_moving))
        self.model.obj.subscribe(self._update_position)
        self.position_updated.connect(self.update_position)
        self.setLayout(box)

    def _update_position(self, *args, value, **newpos):
        self.position_updated.emit(value)

    @Slot(float)
    def update_position(self, value):
        self.position.setText(str(value))


class MotorControl(QWidget):
    position_updated = Signal(float)

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        box = QHBoxLayout()
        self.obj = model.obj
        self.model = model
        self.label = QLabel(model.label)
        box.addWidget(self.label)
        self.lineEdit = QLineEdit()
        self.lineEdit.editingFinished.connect(self.enter_position)
        if hasattr(self.obj, "setpoint"):
            self.setpoint = self.obj.setpoint
        else:
            self.setpoint = self.obj.user_setpoint
        try:
            sp = self.setpoint.get()
        except:
            sp = "Not Connected"
        self.lineEdit.setText(str(sp))
        box.addWidget(self.lineEdit)
        self.position = QLabel("")
        box.addWidget(self.position)
        box.addWidget(OphydByteIndicator(self.obj.motor_is_moving))
        self.obj.subscribe(self._update_position)
        self.position_updated.connect(self.update_position)
        lbutton = QPushButton("<")
        lbutton.clicked.connect(self.tweak_left)
        self.tweakEdit = QLineEdit()
        self.tweakEdit.setText("1")
        rbutton = QPushButton(">")
        rbutton.clicked.connect(self.tweak_right)
        box.addWidget(lbutton)
        box.addWidget(self.tweakEdit)
        box.addWidget(rbutton)
        self.setLayout(box)

    def _update_position(self, *args, value, **newpos):
        self.position_updated.emit(value)

    @Slot(float)
    def update_position(self, value):
        self.position.setText(str(value))

    def enter_position(self):
        newpos = float(self.lineEdit.text())
        self.obj.set(newpos)

    def tweak_left(self):
        current_position = self.obj.position
        step = float(self.tweakEdit.text())
        new_sp = current_position - step
        self.obj.set(new_sp)
        self.lineEdit.setText(str(new_sp))

    def tweak_right(self):
        current_position = self.obj.position
        step = float(self.tweakEdit.text())
        new_sp = current_position + step
        self.obj.set(new_sp)
        self.lineEdit.setText(str(new_sp))
