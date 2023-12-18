from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QStackedWidget,
    QSizePolicy,
)
from qtpy.QtGui import QDoubleValidator, QIntValidator
from qtpy.QtCore import Signal, Qt
from sst_gui.widgets.run_engine_client import QtRePlanQueue
from bluesky_queueserver_api import BPlan


class PlanTabWidget(QWidget):
    def __init__(self, model, parent=None):
        print("Initializing PlanTab")
        super().__init__(parent)

        self.layout = QVBoxLayout(self)
        # Create and add the PlanSubmissionWidget
        self.plan_submission_widget = PlanSubmissionWidget(model, self)
        # self.plan_submission_widget.setParent(self)
        self.layout.addWidget(self.plan_submission_widget)

        # Create and add the _QtReViewer
        self.qt_plan_queue = QtRePlanQueue(model.run_engine)
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)

        self.qt_plan_queue.setSizePolicy(sizePolicy)
        self.layout.addWidget(self.qt_plan_queue)

        print("Finished Initializing PlanTab")


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
                if value in (int, float, str):
                    label = QLabel(key)
                    input_layout.addWidget(label)
                    line_edit = QLineEdit(self)
                    if value == int:
                        line_edit.setValidator(QIntValidator())
                    elif value == float:
                        line_edit.setValidator(QDoubleValidator())
                    input_layout.addWidget(line_edit)
                    self.input_widgets[key] = line_edit
                elif isinstance(value, list):
                    label = QLabel(key)
                    input_layout.addWidget(label)
                    combo_box = QComboBox(self)
                    combo_box.addItem("none")
                    combo_box.addItems(value)
                    input_layout.addWidget(combo_box)
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

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                # remove it from the layout list
                self.layout.removeWidget(widget)
                # remove it from the gui
                widget.setParent(None)


class SampleDialog(QDialog):
    def __init__(self, samples={}, parent=None):
        super().__init__(parent)

        self.list_widget = QListWidget()
        self.sample_keys = list(samples.keys())

        for k, s in samples.items():
            item = QListWidgetItem(f"Sample {k}: {s}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.list_widget.addItem(item)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def get_checked_samples(self):
        checked_samples = []
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).checkState() == Qt.Checked:
                checked_samples.append(self.sample_keys[index])
        return checked_samples


def print_size_in_layout(layout):
    for i in range(layout.count()):
        widget = layout.itemAt(i).widget()
        if widget is not None:
            print_size_info(f"Widget {i} size info:", widget)


def print_size_info(msg, widget):
    print(msg)
    print(f"Size hint: {widget.sizeHint()}")
    print(f"Minimum size hint: {widget.minimumSizeHint()}")
    print(f"Current size: {widget.size()}")
    print(f"Minimum size: {widget.minimumSize()}")
    size_policy = widget.sizePolicy()
    print("Got Size Policy")
    print(
        f"Horizontal size policy: {QSizePolicy.Policy(size_policy.horizontalPolicy())}"
    )
    print(f"Vertical size policy: {QSizePolicy.Policy(size_policy.verticalPolicy())}")


class SampleSelectWidget(QWidget):
    signal_update_samples = Signal(object)
    is_ready = Signal(bool)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        print("Initializing Sample Select")
        self.layout = QHBoxLayout(self)
        self.user_status = model.user_status
        self.signal_update_samples.connect(self.update_samples)
        self.user_status.register_signal("SAMPLE_LIST", self.signal_update_samples)
        self.samples = {}
        self.checked_samples = []

        self.sample_option = QComboBox(self)
        self.sample_selection = QStackedWidget(self)

        self.no_sample = QLabel("(Stay in Place)", self)
        self.one_sample = QComboBox(self)
        self.one_sample.addItem("Select Sample")
        self.one_sample.setItemData(0, "", Qt.UserRole - 1)
        self.one_sample.addItems(self.samples.keys())
        self.one_sample.currentIndexChanged.connect(self.emit_ready)
        self.multi_sample = QPushButton("Sample Select", self)
        self.multi_sample.clicked.connect(self.create_sample_dialog)
        self.dialog_accepted = False

        self.sample_option.addItems(["No Sample", "One Sample", "Multiple Samples"])

        self.sample_selection.addWidget(self.no_sample)
        self.sample_selection.addWidget(self.one_sample)
        self.sample_selection.addWidget(self.multi_sample)

        self.sample_option.currentIndexChanged.connect(
            self.sample_selection.setCurrentIndex
        )
        self.sample_option.currentIndexChanged.connect(self.clear_sample_selection)
        self.sample_selection.currentChanged.connect(self.emit_ready)
        self.layout.addWidget(self.sample_option)
        self.layout.addWidget(self.sample_selection)
        print("Sample Select Initialized")

    def clear_sample_selection(self, *args):
        self.dialog_accepted = False
        self.checked_samples = []

    def create_sample_dialog(self):
        """
        Create a sample dialog and store the checked samples when the dialog is accepted.
        """
        dialog = SampleDialog(self.samples)
        if dialog.exec():
            self.checked_samples = dialog.get_checked_samples()
            if self.checked_samples is not []:
                self.dialog_accepted = True
            else:
                self.dialog_accepted = False
            self.emit_ready()

    def update_samples(self, sample_dict):
        self.samples = sample_dict
        self.one_sample.clear()
        self.one_sample.addItem("Select Sample")
        self.one_sample.setItemData(0, "", Qt.UserRole - 1)
        self.one_sample.addItems(self.samples.keys())

    def get_samples(self):
        if self.sample_option.currentText() == "No Sample":
            return [
                None,
            ]
        elif self.sample_option.currentText() == "One Sample":
            return [
                self.one_sample.currentText(),
            ]
        elif self.sample_option.currentText() == "Multiple Samples":
            return self.checked_samples

    def emit_ready(self):
        ready_status = self.check_ready()
        self.is_ready.emit(ready_status)

    def check_ready(self):
        """
        Check if all selections have been made and return True if they have.
        """
        if self.sample_option.currentText() == "No Sample":
            return True
        elif (
            self.sample_option.currentText() == "One Sample"
            and self.one_sample.currentIndex() != 0
        ):
            return True
        elif (
            self.sample_option.currentText() == "Multiple Samples"
            and self.dialog_accepted
        ):
            return True
        else:
            return False


class XASPlanWidget(PlanWidget):
    signal_update_xas = Signal(object)

    def __init__(self, model, parent=None, **kwargs):
        super().__init__(model, parent, **kwargs)
        print("Initializing XAS")
        self.xas_plans = {}
        self.user_status.register_signal("XAS_PLANS", self.signal_update_xas)
        self.sample_widget = SampleSelectWidget(model, self)
        self.edge_selection = QComboBox(self)
        self.edge_selection.addItem("Select Edge")
        self.edge_selection.setItemData(0, "", Qt.UserRole - 1)
        self.edge_selection.addItems(self.xas_plans.keys())
        self.edge_selection.currentIndexChanged.connect(self.check_plan_ready)
        self.sample_widget.is_ready.connect(self.check_plan_ready)
        self.signal_update_xas.connect(self.update_xas)
        self.basePlanLayout.addWidget(self.sample_widget)
        self.basePlanLayout.addWidget(self.edge_selection)
        print("XAS Initialized")
        # Add all the XAS related methods and widgets here

    def check_plan_ready(self):
        """
        Check if all selections have been made and emit the plan_ready signal if they have.
        """
        print("Checking XAS Plan")
        if self.sample_widget.check_ready() and self.edge_selection.currentIndex() != 0:
            print("XAS Ready to Submit")
            self.plan_ready.emit(True)
        else:
            print("XAS not ready")
            self.plan_ready.emit(False)

    def update_xas(self, plan_dict):
        self.xas_plans = plan_dict
        self.edge_selection.clear()
        self.edge_selection.addItem("Select Edge")
        self.edge_selection.setItemData(0, "", Qt.UserRole - 1)
        self.edge_selection.addItems(self.xas_plans.keys())
        self.widget_updated.emit()

    def submit_plan(self):
        edge = self.edge_selection.currentText()
        samples = self.sample_widget.get_samples()
        params = self.get_params()
        for s in samples:
            item = BPlan(self.xas_plans[edge], sample=s, **params)
            self.run_engine_client.queue_item_add(item=item)


class MovePlanWidget(PlanWidget):
    signal_update_motors = Signal(object)

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        print("Initializing Move")
        self.motors = {}

        self.user_status.register_signal(
            "MOTOR_DESCRIPTIONS", self.signal_update_motors
        )
        self.create_move_modifier()
        self.signal_update_motors.connect(self.update_motors)
        print("Move Initialized")
        # Create and add the move related widgets here

    def update_motors(self, plan_dict):
        inverted_dict = {}
        for key, value in plan_dict.items():
            inverted_dict[value] = key
        self.motors = inverted_dict
        self.noun_selection.clear()
        self.noun_selection.addItems(self.motors.keys())
        print(plan_dict)

    def create_move_modifier(self):
        self.noun_selection = QComboBox(self)
        self.noun_selection.addItems(self.motors.keys())
        self.modifier_selection = QLineEdit(self)
        self.modifier_selection.setValidator(QDoubleValidator())
        self.modifier_selection.editingFinished.connect(self.check_plan_ready)
        self.basePlanLayout.addWidget(self.noun_selection)
        self.basePlanLayout.addWidget(self.modifier_selection)

    def check_plan_ready(self):
        if self.modifier_selection.text() != "":
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        position = float(self.modifier_selection.text())
        item = BPlan("move", motor, position)
        self.run_engine_client.queue_item_add(item=item)


class ScanPlanWidget(PlanWidget):
    signal_update_motors = Signal(object)

    def __init__(self, model, parent=None):
        super().__init__(model, parent)
        print("Initializing Scan")
        self.motors = {}

        self.user_status.register_signal(
            "MOTOR_DESCRIPTIONS", self.signal_update_motors
        )
        self.signal_update_motors.connect(self.update_motors)

        # Create and add the scan related widgets here
        self.create_scan_modifier()
        print("Scan Initialized")

    def update_motors(self, plan_dict):
        inverted_dict = {}
        for key, value in plan_dict.items():
            inverted_dict[value] = key
        self.motors = inverted_dict
        self.noun_selection.clear()
        self.noun_selection.addItems(self.motors.keys())

    def create_scan_modifier(self):
        self.noun_selection = QComboBox(self)
        self.noun_selection.addItems(self.motors.keys())
        self.modifier_input_from = QLineEdit(self)
        self.modifier_input_from.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_from.setValidator(QDoubleValidator())
        self.modifier_input_to = QLineEdit(self)
        self.modifier_input_to.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_to.setValidator(QDoubleValidator())
        self.modifier_input_steps = QLineEdit(self)
        self.modifier_input_steps.editingFinished.connect(self.check_plan_ready)
        self.modifier_input_steps.setValidator(QIntValidator())

        self.basePlanLayout.addWidget(self.noun_selection)
        self.basePlanLayout.addWidget(self.modifier_input_from)
        self.basePlanLayout.addWidget(self.modifier_input_to)
        self.basePlanLayout.addWidget(self.modifier_input_steps)

    def check_plan_ready(self):
        check1 = self.modifier_input_from.text() != ""
        check2 = self.modifier_input_to.text() != ""
        check3 = self.modifier_input_steps.text() != ""
        if check1 and check2 and check3:
            self.plan_ready.emit(True)
        else:
            self.plan_ready.emit(False)

    def submit_plan(self):
        motor_text = self.noun_selection.currentText()
        motor = self.motors[motor_text]
        start = float(self.modifier_input_from.text())
        end = float(self.modifier_input_to.text())
        steps = int(self.modifier_input_steps.text())
        item = BPlan("tes_scan", motor, start, end, steps)
        self.run_engine_client.queue_item_add(item=item)


class PlanSubmissionWidget(QWidget):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        print("Initializing PlanSubmission")
        self.model = model
        self.run_engine_client = model.run_engine
        self.user_status = model.user_status
        self.action_dict = {
            "xas": XASPlanWidget(
                model, parent=self, repeat=int, eslit=float, dwell=float
            ),
            "move": MovePlanWidget(model, parent=self),
            "scan": ScanPlanWidget(model, parent=self),
        }
        print("Initialized Action Dict")
        self.action_widget = QStackedWidget(self)

        # Create and add the action selection combo box
        self.action_prefix = QLabel("Perform", self)
        self.action_selection = QComboBox(self)
        self.action_suffix = QLabel("of", self)

        for k, widget in self.action_dict.items():
            self.action_widget.addWidget(widget)
            self.action_selection.addItem(k)

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.action_prefix)
        self.layout.addWidget(self.action_selection)
        self.layout.addWidget(self.action_suffix)
        print("Actions Added")
        # Create and add the default modifier selection combo box
        self.layout.addWidget(self.action_widget)
        print("Modifier Added")

        # Update the modifier selection options based on the selected action
        self.action_selection.currentIndexChanged.connect(
            self.action_widget.setCurrentIndex
        )

        # Create and add the submit button
        self.submit_button = QPushButton("Submit", self)
        self.submit_button.clicked.connect(self.submit_plan)
        self.submit_button.setEnabled(False)
        self.action_widget.currentChanged.connect(self.update_plan_ready_connection)
        self.update_plan_ready_connection(self.action_widget.currentIndex())
        self.layout.addWidget(self.submit_button)

    def update_plan_ready_connection(self, index):
        """
        Update the connection to the plan_ready signal of the current widget.
        """
        # Disconnect the plan_ready signal of the previous widget
        if hasattr(self, "current_widget") and isinstance(
            self.current_widget, PlanWidget
        ):
            try:
                self.current_widget.plan_ready.disconnect(self.submit_button.setEnabled)
            except TypeError:
                # The signal was not connected
                pass

        # Connect the plan_ready signal of the new widget
        self.current_widget = self.action_widget.widget(index)
        if isinstance(self.current_widget, PlanWidget):
            self.current_widget.plan_ready.connect(self.submit_button.setEnabled)
        self.current_widget.check_plan_ready()

    def submit_plan(self):
        # Get the selected action, noun, and modifier
        selected_widget = self.action_widget.currentWidget()
        selected_widget.submit_plan()
