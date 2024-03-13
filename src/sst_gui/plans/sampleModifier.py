from qtpy.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QComboBox,
    QLineEdit,
    QDialog,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QStackedWidget,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
)

from qtpy.QtCore import Signal, Qt


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
