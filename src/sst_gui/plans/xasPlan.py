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
from bluesky_queueserver_api import BPlan
from .base import PlanWidget
from .sampleModifier import SampleSelectWidget


class XASPlanWidget(PlanWidget):
    signal_update_xas = Signal(object)

    def __init__(self, model, parent=None):
        super().__init__(
            model,
            parent,
            repeat=int,
            eslit=("Exit Slit", float),
            dwell=float,
            group_name=("Group Name", str),
            comment=str,
        )
        print("Initializing XAS")
        self.display_name = "XAS"
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
