from bluesky_widgets.qt.run_engine_client import (
    QtReEnvironmentControls,
    QtReManagerConnection,
    QtReQueueControls,
    QtReExecutionControls,
    QtReStatusMonitor,
    QtRePlanQueue,
    QtRePlanHistory,
    QtReRunningPlan,
    QtRePlanEditor,
    QtReConsoleMonitor,
)
from qtpy.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)


class QueueControlTab(QWidget):
    name = "Queue Control"

    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model.run_engine
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QtReManagerConnection(self.model))
        hbox.addWidget(QtReEnvironmentControls(self.model))
        hbox.addWidget(QtReQueueControls(self.model))
        hbox.addWidget(QtReExecutionControls(self.model))
        hbox.addWidget(QtReStatusMonitor(self.model))

        hbox.addStretch()
        vbox.addLayout(hbox)

        hbox = QHBoxLayout()
        vbox1 = QVBoxLayout()

        # Register plan editor (opening plans in the editor by double-clicking the plan in the table)
        pe = QtRePlanEditor(self.model)
        pq = QtRePlanQueue(self.model)
        pq.registered_item_editors.append(pe.edit_queue_item)

        vbox1.addWidget(pe, stretch=1)
        vbox1.addWidget(pq, stretch=1)
        hbox.addLayout(vbox1)
        vbox2 = QVBoxLayout()
        vbox2.addWidget(QtReRunningPlan(self.model), stretch=1)
        vbox2.addWidget(QtRePlanHistory(self.model), stretch=2)
        hbox.addLayout(vbox2)
        vbox.addLayout(hbox)
        vbox.addWidget(QtReConsoleMonitor(self.model))
        self.setLayout(vbox)
