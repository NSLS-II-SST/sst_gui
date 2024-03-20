from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QLabel,
)
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal


class PlanWidget(QWidget):
    widget_updated = Signal()
    plan_ready = Signal(bool)

    def __init__(self, model, parent=None, **kwargs):
        super().__init__(parent)
        print("Initializing a PlanWidget")
        self.model = model
        self.run_engine_client = model.run_engine
        self.user_status = model.user_status
        self.layout = QVBoxLayout(self)
        self.basePlanLayout = QHBoxLayout()
        self.layout.addLayout(self.basePlanLayout)

        self.input_widgets = {}

        if kwargs:
            print("Initializing PlanWidget params")
            input_layout = QHBoxLayout()
            self.layout.addLayout(input_layout)

            for key, value in kwargs.items():
                if isinstance(value, (list, tuple)):
                    label = QLabel(value[0])
                    value = value[1]
                else:
                    label = QLabel(key)
                if value in (int, float, str):
                    input_layout.addWidget(label)
                    line_edit = QLineEdit(self)
                    line_edit.editingFinished.connect(self.check_plan_ready)
                    if value == int:
                        line_edit.setValidator(QIntValidator())
                    elif value == float:
                        line_edit.setValidator(QDoubleValidator())
                    input_layout.addWidget(line_edit)
                    self.input_widgets[key] = line_edit
                elif isinstance(value, list):
                    input_layout.addWidget(label)
                    combo_box = QComboBox(self)
                    combo_box.addItem("none")
                    combo_box.addItems(value)
                    input_layout.addWidget(combo_box)
                    combo_box.currentIndexChanged.connect(self.check_plan_ready)
                    self.input_widgets[key] = combo_box
        print("Finished initializing PlanWidget")

    def get_params(self):
        """
        Get parameters from the input widgets.

        Returns
        -------
        dict
            A dictionary of parameters.
        """
        params = {}
        for key, widget in self.input_widgets.items():
            if isinstance(widget, QComboBox):
                value = widget.currentText()
            else:
                value = widget.text()
                if value == "":
                    continue
                if isinstance(widget.validator(), QIntValidator):
                    value = int(value)
                elif isinstance(widget.validator(), QDoubleValidator):
                    value = float(value)
            if value not in ("", "none"):
                params[key] = value
        return params

    def check_plan_ready(self):
        params = self.get_params()
        checks = [key in params for key in self.input_widgets.keys()]
        if all(checks):
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                # remove it from the layout list
                self.layout.removeWidget(widget)
                # remove it from the gui
                widget.setParent(None)


class PlanModifier(PlanWidget):
    def __init__(self, model, wrapper, **kwargs):
        self._wrapper = wrapper
        super().__init__(model, **kwargs)

    def get_params(self):
        return self._wrapper, super().get_params()
