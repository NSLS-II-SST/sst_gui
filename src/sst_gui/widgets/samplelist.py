from qtpy.QtWidgets import (
    QTableView,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
)
from qtpy.QtCore import QAbstractTableModel, Qt, Signal, Slot
from bluesky_queueserver_api import BFunc


class SampleTab(QWidget):
    name = "Samples"

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.model = model

        self.file_picker = FilePicker(model.run_engine, parent=self)
        self.layout.addWidget(self.file_picker)
        # Widget 2: QtSampleView
        self.sample_view = QtSampleView(model.user_status, parent=self)
        self.layout.addWidget(self.sample_view)


class FilePicker(QWidget):
    def __init__(self, run_engine_client, parent=None):
        # Widget 1: File picker
        super().__init__(parent)
        self.run_engine_client = run_engine_client
        self.layout = QVBoxLayout(self)
        self.file_picker = QPushButton("Pick a file", self)
        self.file_picker.clicked.connect(self.pick_file)
        self.layout.addWidget(self.file_picker)
        self.selected_file = None

    def pick_file(self):
        fname = QFileDialog.getOpenFileName(self, "Open file")
        if fname[0]:
            self.selected_file = fname[0]
        item = BFunc("load_standard_four_sided_bar", self.selected_file)
        self.run_engine_client._client.function_execute(item=item)


class QtSampleView(QTableView):
    signal_update_widget = Signal(object)

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.signal_update_widget.connect(self.update_md)
        self.model.register_signal("SAMPLE_LIST", self.signal_update_widget)
        self.tableModel = DictTableModel({})
        self.setModel(self.tableModel)

    @Slot(object)
    def update_md(self, samples):
        self.tableModel.update(samples)


class DictTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            key = list(self._data.keys())[index.row()]
            key2 = list(self._data[key].keys())[index.column()]
            return str(self._data[key][key2])

    def rowCount(self, index):
        return len(self._data.keys())

    def columnCount(self, index):
        mincol = None
        for k, v in self._data.items():
            if mincol is None:
                mincol = len(v.keys())
            else:
                mincol = min(len(v.keys()), mincol)
        if mincol is None:
            return 0
        else:
            return mincol

    def update(self, new_data):
        self.beginResetModel()
        self._data = new_data
        self._rows = list(self._data.keys())
        if len(self._rows) > 0:
            for k, v in self._data.items():
                self._columns = list(v.keys())
                break
        self.endResetModel()

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._columns[section])
            if orientation == Qt.Vertical:
                return self._rows[section]
